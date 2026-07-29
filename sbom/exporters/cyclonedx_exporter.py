"""Export SBOM in CycloneDX format."""

import json
import logging
import uuid
from pathlib import Path
from typing import Dict
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

logger = logging.getLogger(__name__)


class CycloneDXExporter:
    """Export SBOM in CycloneDX 1.4 format."""
    
    SPEC_VERSION = "1.4"
    XMLNS = "http://cyclonedx.org/schema/bom/1.4"
    
    def __init__(self, metadata: Dict):
        self.metadata = metadata
    
    def export(self, components: Dict[str, any], output_path: Path) -> None:
        """Export components to CycloneDX format."""
        # Determine format based on extension
        if output_path.suffix.lower() in ['.xml']:
            self._export_xml(components, output_path)
        else:
            # Default to JSON
            self._export_json(components, output_path)
        
        logger.info(f"CycloneDX BOM exported to {output_path}")
    
    def _export_json(self, components: Dict, output_path: Path) -> None:
        """Export as CycloneDX JSON."""
        bom = self._create_bom_structure(components)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(bom, f, indent=2, ensure_ascii=False)
    
    def _export_xml(self, components: Dict, output_path: Path) -> None:
        """Export as CycloneDX XML."""
        root = ET.Element('bom')
        root.set('xmlns', self.XMLNS)
        root.set('serialNumber', f"urn:uuid:{uuid.uuid4()}")
        root.set('version', '1')
        
        # Metadata
        metadata = ET.SubElement(root, 'metadata')
        timestamp = ET.SubElement(metadata, 'timestamp')
        timestamp.text = self.metadata['timestamp']
        
        tools_elem = ET.SubElement(metadata, 'tools')
        tool = ET.SubElement(tools_elem, 'tool')
        tool_name = ET.SubElement(tool, 'name')
        tool_name.text = self.metadata['tool']
        tool_version = ET.SubElement(tool, 'version')
        tool_version.text = self.metadata['tool_version']
        
        # Main component (the project)
        component = ET.SubElement(metadata, 'component')
        component.set('type', 'application')
        comp_name = ET.SubElement(component, 'name')
        comp_name.text = self.metadata['project_name']
        comp_version = ET.SubElement(component, 'version')
        comp_version.text = self.metadata['project_version']
        
        # Components
        components_elem = ET.SubElement(root, 'components')
        
        for comp_name, comp_obj in components.items():
            comp_elem = self._component_to_xml(comp_obj)
            components_elem.append(comp_elem)
        
        # Dependencies
        dependencies_elem = ET.SubElement(root, 'dependencies')
        
        # Root depends on all components
        root_dep = ET.SubElement(dependencies_elem, 'dependency')
        root_dep.set('ref', self._generate_bom_ref(self.metadata['project_name']))
        
        for comp_obj in components.values():
            dep_elem = ET.SubElement(root_dep, 'dependency')
            dep_elem.set('ref', self._generate_bom_ref(comp_obj.name))
        
        # Pretty print and write
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
    
    def _create_bom_structure(self, components: Dict) -> Dict:
        """Create CycloneDX BOM structure."""
        bom = {
            "bomFormat": "CycloneDX",
            "specVersion": self.SPEC_VERSION,
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": self.metadata['timestamp'],
                "tools": [
                    {
                        "name": self.metadata['tool'],
                        "version": self.metadata['tool_version']
                    }
                ],
                "component": {
                    "type": "application",
                    "name": self.metadata['project_name'],
                    "version": self.metadata['project_version'],
                    "bom-ref": self._generate_bom_ref(self.metadata['project_name'])
                }
            },
            "components": [],
            "dependencies": []
        }
        
        # Add components
        for comp_name, component in components.items():
            comp_dict = self._component_to_dict(component)
            bom["components"].append(comp_dict)
        
        # Add dependencies
        root_deps = {
            "ref": self._generate_bom_ref(self.metadata['project_name']),
            "dependsOn": [
                self._generate_bom_ref(comp.name) for comp in components.values()
            ]
        }
        bom["dependencies"].append(root_deps)
        
        # Add dependency entries for each component
        for component in components.values():
            if component.dependencies:
                comp_deps = {
                    "ref": self._generate_bom_ref(component.name),
                    "dependsOn": [self._generate_bom_ref(dep) for dep in component.dependencies]
                }
                bom["dependencies"].append(comp_deps)
        
        return bom
    
    def _component_to_dict(self, component) -> Dict:
        """Convert a component to CycloneDX dictionary format."""
        comp_dict = {
            "type": self._map_component_type(component.component_type),
            "bom-ref": self._generate_bom_ref(component.name),
            "name": component.name,
            "version": component.version
        }
        
        # Add optional fields
        if component.description:
            comp_dict["description"] = component.description
        
        if component.licenses:
            comp_dict["licenses"] = []
            for license_id in component.licenses:
                comp_dict["licenses"].append({
                    "license": {
                        "id": license_id
                    }
                })
        
        if component.purl:
            comp_dict["purl"] = component.purl
        
        if component.cpe:
            comp_dict["cpe"] = component.cpe
        
        if component.supplier:
            comp_dict["supplier"] = {
                "name": component.supplier
            }
        
        if component.homepage:
            comp_dict["externalReferences"] = [
                {
                    "type": "website",
                    "url": component.homepage
                }
            ]
        
        # Add hashes
        if component.checksums:
            comp_dict["hashes"] = []
            for algo, value in component.checksums.items():
                comp_dict["hashes"].append({
                    "alg": self._map_hash_algorithm(algo),
                    "content": value
                })
        
        # Add properties
        if component.properties:
            comp_dict["properties"] = []
            for key, value in component.properties.items():
                comp_dict["properties"].append({
                    "name": key,
                    "value": value
                })
        
        return comp_dict
    
    def _component_to_xml(self, component) -> ET.Element:
        """Convert a component to CycloneDX XML element."""
        comp_elem = ET.Element('component')
        comp_elem.set('type', self._map_component_type(component.component_type))
        comp_elem.set('bom-ref', self._generate_bom_ref(component.name))
        
        # Name and version
        name = ET.SubElement(comp_elem, 'name')
        name.text = component.name
        version = ET.SubElement(comp_elem, 'version')
        version.text = component.version
        
        # Description
        if component.description:
            desc = ET.SubElement(comp_elem, 'description')
            desc.text = component.description
        
        # Licenses
        if component.licenses:
            licenses = ET.SubElement(comp_elem, 'licenses')
            for license_id in component.licenses:
                lic = ET.SubElement(licenses, 'license')
                lic_id = ET.SubElement(lic, 'id')
                lic_id.text = license_id
        
        # Purl
        if component.purl:
            purl = ET.SubElement(comp_elem, 'purl')
            purl.text = component.purl
        
        # External references
        if component.homepage:
            ext_refs = ET.SubElement(comp_elem, 'externalReferences')
            ref = ET.SubElement(ext_refs, 'reference')
            ref.set('type', 'website')
            url = ET.SubElement(ref, 'url')
            url.text = component.homepage
        
        # Hashes
        if component.checksums:
            hashes = ET.SubElement(comp_elem, 'hashes')
            for algo, value in component.checksums.items():
                hash_elem = ET.SubElement(hashes, 'hash')
                hash_elem.set('alg', self._map_hash_algorithm(algo))
                hash_elem.text = value
        
        return comp_elem
    
    def _generate_bom_ref(self, name: str) -> str:
        """Generate a BOM reference ID."""
        # Clean the name to make it a valid reference
        clean_name = name.replace('/', '-').replace('.', '-').replace(' ', '-')
        return f"pkg:{clean_name}"
    
    def _map_component_type(self, comp_type: str) -> str:
        """Map internal component type to CycloneDX type."""
        type_map = {
            'library': 'library',
            'application': 'application',
            'framework': 'framework',
            'source-file': 'file',
            'file': 'file'
        }
        return type_map.get(comp_type, 'library')
    
    def _map_hash_algorithm(self, algo: str) -> str:
        """Map hash algorithm names to CycloneDX format."""
        algo_map = {
            'md5': 'MD5',
            'sha1': 'SHA-1',
            'sha256': 'SHA-256',
            'sha512': 'SHA-512'
        }
        return algo_map.get(algo.lower(), algo.upper())
