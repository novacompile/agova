"""File management and workspace utilities"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import json
import uuid
import shutil

class FileManager:
    def __init__(self, base_workspace: str = "workspace"):
        self.base_workspace = Path(base_workspace)
        self.base_workspace.mkdir(exist_ok=True)
    
    def create_prompt_workspace(self, prompt_name: str = None) -> str:
        """Create a workspace directory with a custom name and UUID"""
        # Generate a short UUID
        short_uuid = str(uuid.uuid4())[:8]
        
        if prompt_name:
            # Clean the prompt name for filesystem
            safe_name = "".join(c for c in prompt_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')[:30]  # Limit length
            if safe_name:
                workspace_name = f"{safe_name}_{short_uuid}"
            else:
                workspace_name = f"prompt_{short_uuid}"
        else:
            workspace_name = f"prompt_{short_uuid}"
        
        workspace_path = self.base_workspace / workspace_name
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (workspace_path / "code").mkdir(exist_ok=True)
        (workspace_path / "research").mkdir(exist_ok=True)
        (workspace_path / "validation").mkdir(exist_ok=True)
        (workspace_path / "debug").mkdir(exist_ok=True)
        
        return str(workspace_path)
    
    def save_results(self, workspace: str, results: Dict[str, Any], query: str):
        """Save all results to the workspace"""
        workspace_path = Path(workspace)
        
        # Save query
        with open(workspace_path / "query.txt", "w", encoding='utf-8') as f:
            f.write(f"Query: {query}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        
        # Save full results as JSON
        with open(workspace_path / "results.json", "w", encoding='utf-8') as f:
            clean_results = self._clean_for_json(results)
            json.dump(clean_results, f, indent=2, ensure_ascii=False)
        
        # Save individual components
        if "research" in results and "results" in results["research"]:
            with open(workspace_path / "research" / "findings.txt", "w", encoding='utf-8') as f:
                f.write(results["research"]["results"])
        
        if "code" in results:
            if "code" in results["code"]:
                with open(workspace_path / "code" / "full_response.txt", "w", encoding='utf-8') as f:
                    f.write(results["code"]["code"])
            
            if "code_blocks" in results["code"]:
                for i, block in enumerate(results["code"]["code_blocks"]):
                    ext = self._get_extension(block.get("language", ""))
                    filename = f"solution_{i+1}{ext}"
                    with open(workspace_path / "code" / filename, "w", encoding='utf-8') as f:
                        f.write(block["code"])
        
        if "validation" in results:
            with open(workspace_path / "validation" / "report.txt", "w", encoding='utf-8') as f:
                f.write(str(results["validation"].get("validation", "")))
        
        if "debug" in results:
            with open(workspace_path / "debug" / "fixed_solution.txt", "w", encoding='utf-8') as f:
                f.write(str(results["debug"].get("fixed_solution", "")))
        
        if "final_validation" in results:
            with open(workspace_path / "validation" / "final_report.txt", "w", encoding='utf-8') as f:
                f.write(str(results["final_validation"].get("validation", "")))
        
        # Save file tree
        self.save_file_tree(workspace_path)
    
    def save_file_tree(self, workspace_path: Path):
        """Generate and save file tree visualization"""
        tree = self._generate_tree(workspace_path)
        with open(workspace_path / "file_tree.txt", "w", encoding='utf-8') as f:
            f.write("FILE TREE\n")
            f.write("="*50 + "\n\n")
            f.write(tree)
    
    def _generate_tree(self, path: Path, prefix: str = "") -> str:
        """Generate a visual file tree"""
        if not path.exists():
            return ""
        tree = f"{prefix}{path.name}/\n"
        try:
            contents = sorted(path.iterdir())
            for i, item in enumerate(contents):
                is_last = i == len(contents) - 1
                current_prefix = prefix + ("└── " if is_last else "├── ")
                next_prefix = prefix + ("    " if is_last else "│   ")
                if item.is_dir():
                    tree += current_prefix + self._generate_tree(item, next_prefix)
                else:
                    size = item.stat().st_size
                    size_str = self._format_size(size)
                    tree += f"{current_prefix}{item.name} ({size_str})\n"
        except PermissionError:
            pass
        return tree
    
    def _get_extension(self, language: str) -> str:
        extensions = {
            "python": ".py", "javascript": ".js", "html": ".html",
            "css": ".css", "java": ".java", "cpp": ".cpp", "go": ".go",
            "rust": ".rs", "sql": ".sql", "bash": ".sh", "json": ".json"
        }
        return extensions.get(language.lower(), ".txt")
    
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _clean_for_json(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            return {str(k): self._clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_for_json(v) for v in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return str(obj)
