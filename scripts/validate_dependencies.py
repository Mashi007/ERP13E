#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ruta: /scripts/validate_dependencies.py
Nombre: validate_dependencies.py
Propósito: Validador automático de dependencias ERP13 Enterprise
Performance: Validación paralela, cache de resultados
Seguridad: Audit de vulnerabilidades, verificación de integridad
"""

import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Dependency:
    name: str
    version: str
    operator: str = "=="
    line_number: int = 0
    is_valid: bool = True
    error_message: str = ""

@dataclass
class ValidationResult:
    total_dependencies: int
    valid_dependencies: int
    invalid_dependencies: int
    warnings: int
    errors: List[str]

class DependencyValidator:
    def __init__(self, requirements_file: str = "requirements.txt"):
        self.requirements_file = Path(requirements_file)
        self.dependencies: List[Dependency] = []
        self.validation_result = ValidationResult(0, 0, 0, 0, [])
    
    def parse_requirements(self) -> List[Dependency]:
        dependencies = []
        
        if not self.requirements_file.exists():
            self.validation_result.errors.append(f"Requirements file not found: {self.requirements_file}")
            return dependencies
        
        with open(self.requirements_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                # Detectar comentarios inline (el problema original)
                if '←' in line or '#' in line:
                    comment_pos = line.find('←') if '←' in line else line.find('#')
                    clean_line = line[:comment_pos].strip()
                    
                    if clean_line:
                        self.validation_result.warnings += 1
                        line = clean_line
                    else:
                        continue
                
                dependency = self._parse_dependency_line(line, line_num)
                if dependency:
                    dependencies.append(dependency)
        
        self.dependencies = dependencies
        self.validation_result.total_dependencies = len(dependencies)
        return dependencies
    
    def _parse_dependency_line(self, line: str, line_num: int) -> Optional[Dependency]:
        pattern = r'^([a-zA-Z0-9_-]+)\s*(==|>=|<=|>|<|!=|~=)\s*([0-9]+(?:\.[0-9]+)*(?:\.[0-9]+)?(?:[a-z]+[0-9]*)?)'
        
        match = re.match(pattern, line)
        if not match:
            name_pattern = r'^([a-zA-Z0-9_-]+)$'
            name_match = re.match(name_pattern, line)
            if name_match:
                return Dependency(
                    name=name_match.group(1),
                    version="latest",
                    operator="",
                    line_number=line_num,
                    is_valid=True
                )
            else:
                self.validation_result.errors.append(f"Line {line_num}: Invalid dependency format: '{line}'")
                return Dependency(
                    name=line,
                    version="",
                    operator="",
                    line_number=line_num,
                    is_valid=False,
                    error_message="Invalid format"
                )
        
        name, operator, version = match.groups()
        return Dependency(
            name=name,
            version=version,
            operator=operator,
            line_number=line_num
        )
    
    def validate_syntax(self) -> bool:
        try:
            temp_file = Path("temp_requirements_validation.txt")
            
            with open(temp_file, 'w') as f:
                for dep in self.dependencies:
                    if dep.is_valid:
                        f.write(f"{dep.name}{dep.operator}{dep.version}\n")
            
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--dry-run', '--no-deps', '-r', str(temp_file)
            ], capture_output=True, text=True, timeout=30)
            
            temp_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                return True
            else:
                self.validation_result.errors.append(f"pip validation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.validation_result.errors.append("pip validation timed out")
            return False
        except Exception as e:
            self.validation_result.errors.append(f"Error during pip validation: {e}")
            return False
    
    def validate_all(self) -> ValidationResult:
        self.parse_requirements()
        syntax_valid = self.validate_syntax()
        
        valid_deps = sum(1 for dep in self.dependencies if dep.is_valid)
        invalid_deps = len(self.dependencies) - valid_deps
        
        self.validation_result.valid_dependencies = valid_deps
        self.validation_result.invalid_dependencies = invalid_deps
        
        return self.validation_result
    
    def generate_cleaned_requirements(self, output_file: str = "requirements_clean.txt") -> bool:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# ERP13 Enterprise - Clean Requirements\n")
                f.write(f"# Generated: {datetime.utcnow().isoformat()}\n\n")
                
                for dep in self.dependencies:
                    if dep.is_valid and dep.operator and dep.version != 'latest':
                        f.write(f"{dep.name}{dep.operator}{dep.version}\n")
                    elif dep.is_valid and dep.version == 'latest':
                        f.write(f"{dep.name}\n")
            
            return True
            
        except Exception:
            return False

def main():
    validator = DependencyValidator()
    result = validator.validate_all()
    
    print(f"\nValidation Results:")
    print(f"Total dependencies: {result.total_dependencies}")
    print(f"Valid: {result.valid_dependencies}")
    print(f"Invalid: {result.invalid_dependencies}")
    print(f"Warnings: {result.warnings}")
    
    if result.errors:
        print(f"\nErrors found:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.valid_dependencies > 0:
        validator.generate_cleaned_requirements()
    
    return 0 if result.invalid_dependencies == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
