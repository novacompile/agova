"""Orchestrator agent to coordinate all other agents"""
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
from .base_agent import BaseAgent
from .researcher import ResearcherAgent
from .coder import CoderAgent
from .validator import ValidatorAgent
from .debugger import DebuggerAgent
from utils.file_manager import FileManager
from utils.config_manager import ConfigManager

class OrchestratorAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Orchestrator", "Task Coordination", console)
        self.config_manager = ConfigManager()
        self.researcher = ResearcherAgent(console)
        self.coder = CoderAgent(console)
        self.validator = ValidatorAgent(console)
        self.debugger = DebuggerAgent(console)
        self.file_manager = FileManager()
        
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate the entire workflow"""
        query = task.get("query", "")
        prompt_id = task.get("prompt_id", "1")
        
        self.log(f"🚀 Starting workflow for: '{query}'", "bold blue")
        self.add_to_context("task", f"Orchestration: {query}")
        
        # Create workspace for this prompt
        workspace = self.file_manager.create_prompt_workspace(prompt_id)
        self.log(f"📁 Workspace created: {workspace}", "dim")
        
        # Display workflow plan
        self._display_workflow_plan(query)
        
        # Phase 1: Research
        if self.config_manager.get("display.show_agent_transitions", True):
            self.log("📚 Phase 1: Research", "cyan")
        
        research_result = await self.researcher.execute({"query": query})
        
        if research_result.get("status") == "error":
            self.log("❌ Workflow failed at research phase", "red")
            return research_result
        
        # Determine if coding is needed
        needs_code = self._needs_coding(query)
        
        final_result = {
            "research": research_result,
            "workspace": workspace,
            "query": query,
            "prompt_id": prompt_id,
            "timestamp": datetime.now().isoformat()
        }
        
        if needs_code:
            # Phase 2: Generate code
            if self.config_manager.get("display.show_agent_transitions", True):
                self.log("💻 Phase 2: Code Generation", "blue")
            
            code_result = await self.coder.execute({
                "requirements": query,
                "research_results": research_result.get("results", "")
            })
            
            if code_result.get("status") == "error":
                self.log("❌ Workflow failed at code generation phase", "red")
                final_result["code"] = code_result
                self.file_manager.save_results(workspace, final_result, query)
                return final_result
            
            final_result["code"] = code_result
            
            # Phase 3: Validate (if auto_validate is enabled)
            if self.config_manager.get("agents.auto_validate", True):
                if self.config_manager.get("display.show_agent_transitions", True):
                    self.log("🔍 Phase 3: Validation", "yellow")
                
                validation_result = await self.validator.execute({
                    "query": query,
                    "research_results": research_result.get("results", ""),
                    "code": code_result.get("code", "")
                })
                
                final_result["validation"] = validation_result
                
                # Phase 4: Debug if needed (if auto_debug is enabled)
                if (not validation_result.get("passed", False) and 
                    self.config_manager.get("agents.auto_debug", True)):
                    
                    if self.config_manager.get("display.show_agent_transitions", True):
                        self.log("🐛 Phase 4: Debugging", "magenta")
                    
                    debug_result = await self.debugger.execute({
                        "query": query,
                        "code": code_result.get("code", ""),
                        "validation_results": validation_result.get("validation", ""),
                        "research_results": research_result.get("results", "")
                    })
                    
                    final_result["debug"] = debug_result
                    
                    # Re-validate after debugging
                    if self.config_manager.get("display.show_agent_transitions", True):
                        self.log("🔍 Phase 5: Re-validation", "yellow")
                    
                    final_validation = await self.validator.execute({
                        "query": query,
                        "research_results": research_result.get("results", ""),
                        "code": debug_result.get("fixed_solution", "")
                    })
                    
                    final_result["final_validation"] = final_validation
            else:
                self.log("⏭️ Validation skipped (auto_validate disabled)", "dim")
        
        # Save results to workspace
        self.file_manager.save_results(workspace, final_result, query)
        
        # Display final summary
        self._display_summary(final_result, workspace)
        
        self.add_to_history("orchestration", {"status": "success"})
        final_result["status"] = "success"
        
        return final_result
    
    def _needs_coding(self, query: str) -> bool:
        """Determine if the query requires coding"""
        coding_keywords = [
            "program", "code", "script", "function", "app", "application",
            "make", "create", "build", "develop", "implement", "automate",
            "write", "generate", "design", "construct", "produce"
        ]
        return any(keyword in query.lower() for keyword in coding_keywords)
    
    def _display_workflow_plan(self, query: str):
        """Display the planned workflow"""
        needs_code = self._needs_coding(query)
        
        table = Table(title="📋 Workflow Plan", show_header=True, header_style="bold magenta")
        table.add_column("Phase", style="cyan", width=10)
        table.add_column("Agent", style="green", width=20)
        table.add_column("Task", style="white")
        
        table.add_row("1", "🔍 Researcher", "Gather information and context")
        
        if needs_code:
            table.add_row("2", "💻 Coder", "Generate code and solution")
            
            if self.config_manager.get("agents.auto_validate", True):
                table.add_row("3", "✅ Validator", "Validate solution correctness")
                
                if self.config_manager.get("agents.auto_debug", True):
                    table.add_row("4*", "🐛 Debugger", "Fix issues (if validation fails)")
                    table.add_row("5*", "✅ Validator", "Re-validate after fixes")
        
        self.console.print(table)
        self.console.print("[dim]* Conditional phases[/dim]\n")
    
    def _display_summary(self, result: Dict[str, Any], workspace: str):
        """Display final summary"""
        # Calculate total tokens used
        total_tokens = 0
        for key in ["research", "code", "validation", "debug", "final_validation"]:
            if key in result and "usage" in result[key]:
                total_tokens += result[key]["usage"].get("total_tokens", 0)
        
        # Determine final status
        if "final_validation" in result:
            final_status = "✅ PASSED" if result["final_validation"].get("passed", False) else "⚠️ NEEDS REVIEW"
        elif "validation" in result:
            final_status = "✅ PASSED" if result["validation"].get("passed", False) else "⚠️ NEEDS REVIEW"
        else:
            final_status = "✅ COMPLETED"
        
        summary_text = f"""
[bold]Query:[/bold] {result.get('query', 'N/A')}
[bold]Workspace:[/bold] {workspace}
[bold]Final Status:[/bold] {final_status}

[bold]Phases Completed:[/bold]
• 🔍 Research: {'✅' if 'research' in result else '❌'}
• 💻 Code: {'✅' if 'code' in result else '⏭️ Skipped'}
• ✅ Validation: {'✅' if 'validation' in result else '⏭️ Skipped'}
• 🐛 Debug: {'✅' if 'debug' in result else '⏭️ Not needed'}
• ✅ Final Validation: {'✅' if 'final_validation' in result else '⏭️ Not needed'}

[bold]Total Tokens Used:[/bold] {total_tokens:,}
[bold]Timestamp:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.console.print(Panel.fit(
            summary_text,
            title="🎯 Workflow Summary",
            border_style="green" if "PASSED" in final_status else "yellow"
        ))
