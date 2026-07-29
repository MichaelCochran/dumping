"""Export SBOM in SPDX format."""

import json
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class SPDXExporter:
    """Export SBOM in SPDX 2.3 format."""
    
    SPDX_VERSION = "SPDX-2.3"
    DATA_LICENSE = "CC0-1.0"
    
    def __init__(self, metadata: Dict):
        self.metadata = metadata
    
    def export(self, components: Dict[str, any], output_path: Path) -> None:
        """Export components to SPDX format."""
        spdx_doc = self._create_spdx_document(components)
        
        # Determine output format based on extension
        if output_path.suffix.lower() in ['.json']:
            self._write_json(spdx_doc, output_path)
        else:
            # Default to JSON
            self._write_json(spdx_doc, output_path)
        
        logger.info(f"SPDX document exported to {output_path}")
    
    def _create_spdx_document(self, components: Dict) -> Dict:
        """Create SPDX document structure."""
        doc_namespace = f"https://sbom.example.com/{self.metadata['project_name']}/{self.metadata['timestamp']}"
        
        spdx_doc = {
            "spdxVersion": self.SPDX_VERSION,
            "dataLicense": self.DATA_LICENSE,
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": f"{self.metadata['project_name']} SBOM",
            "documentNamespace": doc_namespace,
            "creationInfo": {
                "created": self.metadata['timestamp'],
                "creators": [
                    f"Tool: {self.metadata['tool']}-{self.metadata['tool_version']}"
                ],
                "licenseListVersion": "3.21"
            },
            "packages": [],
            "relationships": []
        }
        
        # Add root package (the project itself)
        root_package = {
            "SPDXID": "SPDXRef-Package-Root",
            "name": self.metadata['project_name'],
            "versionInfo": self.metadata['project_version'],
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": True,
            "copyrightText": "NOASSERTION"
        }
        spdx_doc["packages"].append(root_package)
        
        # Add root relationship
        spdx_doc["relationships"].append({
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relationshipType": "DESCRIBES",
            "relatedSpdxElement": "SPDXRef-Package-Root"
        })
        
        # Add each component as a package
        for idx, (comp_name, component) in enumerate(components.items(), start=1):
            package = self._component_to_spdx_package(component, idx)
            spdx_doc["packages"].append(package)
            
            # Add dependency relationship
            spdx_doc["relationships"].append({
                "spdxElementId": "SPDXRef-Package-Root",
                "relationshipType": "DEPENDS_ON",
                "relatedSpdxElement": package["SPDXID"]
            })
        
        return spdx_doc
    
    def _component_to_spdx_package(self, component, idx: int) -> Dict:
        """Convert a component to an SPDX package."""
        # Create a valid SPDX ID
        safe_name = component.name.replace('/', '-').replace('.', '-').replace(' ', '-')
        spdx_id = f"SPDXRef-Package-{safe_name}-{idx}"
        
        package = {
            "SPDXID": spdx_id,
            "name": component.name,
            "versionInfo": component.version,
            "downloadLocation": component.homepage if component.homepage else "NOASSERTION",
            "filesAnalyzed": False,
            "copyrightText": "NOASSERTION"
        }
        
        # Add supplier if available
        if component.supplier:
            package["supplier"] = f"Organization: {component.supplier}"
        
        # Add description if available
        if component.description:
            package["summary"] = component.description
        
        # Add license information
        if component.licenses:
            if len(component.licenses) == 1:
                package["licenseConcluded"] = list(component.licenses)[0]
            else:
                # Multiple licenses - use OR operator
                license_expr = " OR ".join(sorted(component.licenses))
                package["licenseConcluded"] = license_expr
            package["licenseDeclared"] = package["licenseConcluded"]
        else:
            package["licenseConcluded"] = "NOASSERTION"
            package["licenseDeclared"] = "NOASSERTION"
        
        # Add checksums if available
        if component.checksums:
            package["checksums"] = []
            for algo, value in component.checksums.items():
                package["checksums"].append({
                    "algorithm": algo.upper(),
                    "checksumValue": value
                })
        
        # Add external references
        if component.purl:
            if "externalRefs" not in package:
                package["externalRefs"] = []
            package["externalRefs"].append({
                "referenceCategory": "PACKAGE-MANAGER",
                "referenceType": "purl",
                "referenceLocator": component.purl
            })
        
        if component.cpe:
            if "externalRefs" not in package:
                package["externalRefs"] = []
            package["externalRefs"].append({
                "referenceCategory": "SECURITY",
                "referenceType": "cpe23Type",
                "referenceLocator": component.cpe
            })
        
        return package
    
    def _write_json(self, spdx_doc: Dict, output_path: Path) -> None:
        """Write SPDX document as JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(spdx_doc, f, indent=2, ensure_ascii=False)
    
    def _write_tagvalue(self, spdx_doc: Dict, output_path: Path) -> None:
        """Write SPDX document in tag-value format."""
        with open(output_path, 'w', encoding='utf-8') as f:
            # Document creation info
            f.write(f"SPDXVersion: {spdx_doc['spdxVersion']}\n")
            f.write(f"DataLicense: {spdx_doc['dataLicense']}\n")
            f.write(f"SPDXID: {spdx_doc['SPDXID']}\n")
            f.write(f"DocumentName: {spdx_doc['name']}\n")
            f.write(f"DocumentNamespace: {spdx_doc['documentNamespace']}\n")
            
            # Creation info
            creation_info = spdx_doc['creationInfo']
            f.write(f"Creator: {creation_info['creators'][0]}\n")
            f.write(f"Created: {creation_info['created']}\n")
            
            # Packages
            for package in spdx_doc['packages']:
                f.write("\n")
                f.write(f"PackageName: {package['name']}\n")
                f.write(f"SPDXID: {package['SPDXID']}\n")
                f.write(f"PackageVersion: {package['versionInfo']}\n")
                f.write(f"PackageDownloadLocation: {package['downloadLocation']}\n")
                f.write(f"FilesAnalyzed: {str(package['filesAnalyzed']).lower()}\n")
                f.write(f"PackageLicenseConcluded: {package['licenseConcluded']}\n")
                f.write(f"PackageLicenseDeclared: {package['licenseDeclared']}\n")
                f.write(f"PackageCopyrightText: {package['copyrightText']}\n")
                
                if 'supplier' in package:
                    f.write(f"PackageSupplier: {package['supplier']}\n")
                
                if 'summary' in package:
                    f.write(f"PackageSummary: {package['summary']}\n")
                
                if 'checksums' in package:
                    for checksum in package['checksums']:
                        f.write(f"PackageChecksum: {checksum['algorithm']}: {checksum['checksumValue']}\n")
                
                if 'externalRefs' in package:
                    for ref in package['externalRefs']:
                        f.write(f"ExternalRef: {ref['referenceCategory']} {ref['referenceType']} {ref['referenceLocator']}\n")
            
            # Relationships
            f.write("\n")
            for rel in spdx_doc['relationships']:
                f.write(f"Relationship: {rel['spdxElementId']} {rel['relationshipType']} {rel['relatedSpdxElement']}\n")
