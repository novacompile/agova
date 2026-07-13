"""File management and workspace utilities"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import json
import shutil

class FileManager:
    def __init__(self, base_workspace: str = "workspace"):
        self.base_workspace = Path(base_workspace)
        self.base_workspace.mkdir(exist_ok=True)
        self.prompt_counter = self._load_counter()
    
    def _load_counter(self) -> int:
        """Load the prompt counter"""
        counter_file = self.base_workspace / "counter.json"
        if counter_file.exists():
            try:
                with open(counter_file) as f:
                    return json.load(f).get("counter", 0)
            except:
                return 0
        return 0
    
    def _save_counter(self):
        """Save the prompt counter"""
        self.prompt_counter += 1
        with open(self.base_workspace / "counter.json", "w") as f:
            json.dump({"counter": self.prompt_counter}, f)
    
    def create_prompt_workspace(self, prompt_id: Optional[str] = None) -> str:
        """Create a workspace directory for a prompt"""
        if not prompt_id:
            self._save_counter()
            prompt_id = str(self.prompt_counter)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workspace_name = f"prompt_{prompt_id}_{timestamp}"
        workspace_path = self.base_workspace / workspace_name
        
        # Create directory structure
        workspace_path.mkdir(parents=True, exist_ok=True)
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
            f.write(f"Prompt ID: {results.get('prompt_id', 'N/A')}\n")
        
        # Save full results as JSON
        with open(workspace_path / "results.json", "w", encoding='utf-8') as f:
            clean_results = self._clean_for_json(results)
            json.dump(clean_results, f, indent=2, ensure_ascii=False)
        
        # Save individual components
        if "research" in results and "results" in results["research"]:
            with open(workspace_path / "research" / "findings.txt", "w", encoding='utf-8') as f:
                f.write(results["research"]["results"])
        
        if "code" in results:
            # Save full code response
            if "code" in results["code"]:
                with open(workspace_path / "code" / "full_response.txt", "w", encoding='utf-8') as f:
                    f.write(results["code"]["code"])
            
            # Save individual code blocks
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
        
        # Save file tree visualization
        self.save_file_tree(workspace_path)
        
        # Save a README
        self._save_readme(workspace_path, results, query)
    
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
            tree += f"{prefix}└── [Permission Denied]\n"
        
        return tree
    
    def _save_readme(self, workspace_path: Path, results: Dict[str, Any], query: str):
        """Save a README file for the workspace"""
        readme_content = f"""# Workspace for Prompt

**Query:** {query}
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Prompt ID:** {results.get('prompt_id', 'N/A')}

## Contents

### Research
- `research/findings.txt` - Research findings and information gathered

### Code
- `code/` - Generated code and solutions
- `code/full_response.txt` - Complete code generation response

### Validation
- `validation/report.txt` - Initial validation report
- `validation/final_report.txt` - Final validation report (if re-validated)

### Debug
- `debug/fixed_solution.txt` - Debugged and fixed solution (if debugging was needed)

### Other Files
- `query.txt` - Original query
- `results.json` - Complete results in JSON format
- `file_tree.txt` - Visual file tree of workspace

---
Generated by Multi-Agent AI System
"""
        with open(workspace_path / "README.md", "w", encoding='utf-8') as f:
            f.write(readme_content)
    
    def _get_extension(self, language: str) -> str:
        """Get file extension based on language"""
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "html": ".html",
            "css": ".css",
            "java": ".java",
            "cpp": ".cpp",
            "c": ".c",
            "ruby": ".rb",
            "go": ".go",
            "rust": ".rs",
            "sql": ".sql",
            "bash": ".sh",
            "yaml": ".yml",
            "json": ".json",
            "markdown": ".md",
            "text": ".txt"
        }
        return extensions.get(language.lower(), ".txt")
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _clean_for_json(self, obj: Any) -> Any:
        """Clean object for JSON serialization"""
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
    
    def cleanup_old_workspaces(self, max_age_days: int = 30):
        """Clean up workspaces older than specified days"""
        cutoff = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        for workspace_dir in self.base_workspace.iterdir():
            if workspace_dir.is_dir() and workspace_dir.name.startswith("prompt_"):
                if workspace_dir.stat().st_mtime < cutoff:
                    shutil.rmtree(workspace_dir)
                    print(f"🗑️  Removed old workspace: {workspace_dir.name}")
    
    def list_workspaces(self) -> list:
        """List all workspaces"""
        workspaces = []
        for workspace_dir in self.base_workspace.iterdir():
            if workspace_dir.is_dir() and workspace_dir.name.startswith("prompt_"):
                workspaces.append({
                    "name": workspace_dir.name,
                    "created": datetime.fromtimestamp(workspace_dir.stat().st_ctime).isoformat(),
                    "size": sum(f.stat().st_size for f in workspace_dir.rglob('*') if f.is_file())
                })
        return sorted(workspaces, key=lambda x: x["created"], reverse=True)
