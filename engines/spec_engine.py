import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime
import json
import logging

class SpecEngine:
    """Engine for generating and managing specification documents"""
    
    def __init__(self, ai_service):
        self.ai_service = ai_service
        self.logger = logging.getLogger(__name__)
        
        # OpenFlux system prompt for consistent behavior
        self.openflux_system_prompt = """You are OpenFlux, an AI assistant and IDE built to assist developers.

When users ask about OpenFlux, respond with information about yourself in first person.

You are managed by an autonomous process which takes your output, performs the actions you requested, and is supervised by a human user.

You talk like a human, not like a bot. You reflect the user's input style in your responses.

# Response style
- We are knowledgeable. We are not instructive. In order to inspire confidence in the programmers we partner with, we've got to bring our expertise and show we know our Java from our JavaScript. But we show up on their level and speak their language, though never in a way that's condescending or off-putting.
- Speak like a dev — when necessary. Look to be more relatable and digestible in moments where we don't need to rely on technical language or specific vocabulary to get across a point.
- Be decisive, precise, and clear. Lose the fluff when you can.
- We are supportive, not authoritative. Coding is hard work, we get it. That's why our tone is also grounded in compassion and understanding so every programmer feels welcome and comfortable using OpenFlux.
- Use positive, optimistic language that keeps OpenFlux feeling like a solutions-oriented space.
- Stay warm and friendly as much as possible. We're not a cold tech company; we're a companionable partner, who always welcomes you and sometimes cracks a joke or two.
- Be concise and direct in your responses
- Don't repeat yourself, saying the same message over and over, or similar messages is not always helpful, and can look you're confused.
- Prioritize actionable information over general explanations
- Use bullet points and formatting to improve readability when appropriate
- Include relevant code snippets, CLI commands, or configuration examples
- Explain your reasoning when making recommendations"""
    
    def create_requirements(self, feature_description: str, codebase_context: Dict = None) -> str:
        """Generate EARS-format requirements from feature description"""
        
        context_info = ""
        if codebase_context:
            context_info = f"""
            
Codebase Context:
- Languages: {', '.join(codebase_context.get('languages', []))}
- File Count: {codebase_context.get('file_count', 0)}
- Architecture Insights: {codebase_context.get('analysis', 'No analysis available')[:500]}...
"""
        
        requirements_prompt = f"""Generate detailed requirements in EARS format (Easy Approach to Requirements Syntax) for the following feature:

Feature Description: {feature_description}
{context_info}

Please format the requirements document with:

# Requirements Document

## Introduction
[Brief summary of the feature and its purpose]

## Requirements

### Requirement 1
**User Story:** As a [role], I want [feature], so that [benefit]

#### Acceptance Criteria
1. WHEN [event] THEN [system] SHALL [response]
2. IF [precondition] THEN [system] SHALL [response]
3. WHEN [event] AND [condition] THEN [system] SHALL [response]

### Requirement 2
[Continue with additional requirements...]

Focus on:
- User experience and workflows
- Technical constraints and edge cases
- Security and performance considerations
- Integration requirements
- Error handling scenarios

Make the requirements specific, testable, and implementable."""

        try:
            return self.ai_service.generate_text(requirements_prompt, self.openflux_system_prompt)
        except Exception as e:
            self.logger.error(f"Requirements generation failed: {e}")
            raise e
    
    def generate_design(self, requirements: str, codebase_context: Dict = None) -> str:
        """Generate design document from requirements"""
        
        context_info = ""
        if codebase_context:
            context_info = f"""
            
Existing Codebase Context:
- Languages: {', '.join(codebase_context.get('languages', []))}
- File Count: {codebase_context.get('file_count', 0)}
- Current Architecture: {codebase_context.get('analysis', 'No analysis available')[:500]}...
"""
        
        design_prompt = f"""Create a comprehensive design document based on these requirements:

{requirements}
{context_info}

Please format the design document with these sections:

# Design Document

## Overview
[High-level summary of the solution approach]

## Architecture
[System architecture with Mermaid diagrams where appropriate]

```mermaid
graph TB
    [Include relevant architecture diagrams]
```

## Components and Interfaces
[Detailed component breakdown with interfaces]

## Data Models
[Data structures, schemas, and relationships]

## Error Handling
[Error scenarios and handling strategies]

## Testing Strategy
[Approach to testing and validation]

## Security Considerations
[Security requirements and implementation approach]

## Performance Considerations
[Performance requirements and optimization strategies]

Focus on:
- Scalable and maintainable architecture
- Clear separation of concerns
- Integration with existing systems
- Best practices and patterns
- Technical implementation details"""

        try:
            return self.ai_service.generate_text(design_prompt, self.openflux_system_prompt)
        except Exception as e:
            self.logger.error(f"Design generation failed: {e}")
            raise e
    
    def create_task_list(self, design: str, requirements: str = None) -> str:
        """Generate implementation tasks from design document in Kiro markdown format"""
        
        requirements_context = ""
        if requirements:
            requirements_context = f"\n\nRequirements Context:\n{requirements[:1000]}..."
        
        tasks_prompt = f"""Convert this design into actionable implementation tasks in Kiro markdown format:

{design}
{requirements_context}

Generate tasks using this EXACT format:

# Implementation Plan

- [ ] 1. Main task title
  - [ ] 1.1 Sub-task title
    - Detailed description of what needs to be implemented
    - Specific files or components to create/modify
    - Technical implementation details
    - _Requirements: 1.1, 2.3_

  - [ ] 1.2 Another sub-task title
    - Implementation details
    - Code changes needed
    - _Requirements: 2.1_

- [ ] 2. Second main task title
  - [ ] 2.1 Sub-task for second main task
    - Implementation details
    - _Requirements: 3.1_

IMPORTANT FORMATTING RULES:
- Use "- [ ]" for unchecked tasks (not "- [x]")
- Use hierarchical numbering (1, 1.1, 1.2, 2, 2.1, etc.)
- Include requirement references as "_Requirements: X.X, Y.Y_"
- Add detailed implementation descriptions under each task
- Focus ONLY on coding tasks that involve writing, modifying, or testing code
- Each task should build incrementally on previous tasks
- Maximum of 2 levels of hierarchy (main tasks and sub-tasks)

Focus on:
- Coding tasks that can be executed by developers
- Test-driven development approach
- Incremental implementation steps
- Specific file/component references
- Building functionality step by step

Avoid:
- User testing or feedback gathering
- Deployment or infrastructure tasks
- Business process changes
- Marketing or communication tasks

Each task should be concrete enough that a developer can execute it without additional clarification."""

        try:
            response = self.ai_service.generate_text(tasks_prompt, self.openflux_system_prompt)
            return response
                
        except Exception as e:
            self.logger.error(f"Task generation failed: {e}")
            raise e
    
    def update_document(self, doc_type: str, content: str, version: int = 1) -> bool:
        """Update specification document in session state"""
        try:
            timestamp = datetime.now().isoformat()
            
            doc_data = {
                "content": content,
                "version": version,
                "updated_at": timestamp,
                "doc_type": doc_type
            }
            
            # Store in session state
            if doc_type == "requirements":
                st.session_state.requirements_doc = content
                st.session_state.requirements_data = doc_data
            elif doc_type == "design":
                st.session_state.design_doc = content
                st.session_state.design_data = doc_data
            elif doc_type == "tasks":
                st.session_state.task_list = content
                st.session_state.tasks_data = doc_data
            
            return True
            
        except Exception as e:
            self.logger.error(f"Document update failed: {e}")
            return False
    
    def get_document_status(self, doc_type: str) -> Dict:
        """Get status information for a document type"""
        status_map = {
            "requirements": {
                "exists": bool(st.session_state.get("requirements_doc")),
                "content": st.session_state.get("requirements_doc", ""),
                "data": st.session_state.get("requirements_data", {})
            },
            "design": {
                "exists": bool(st.session_state.get("design_doc")),
                "content": st.session_state.get("design_doc", ""),
                "data": st.session_state.get("design_data", {})
            },
            "tasks": {
                "exists": bool(st.session_state.get("task_list")),
                "content": st.session_state.get("task_list", ""),
                "data": st.session_state.get("tasks_data", {})
            }
        }
        
        return status_map.get(doc_type, {"exists": False, "content": "", "data": {}})
    
    def validate_requirements(self, requirements: str) -> Dict:
        """Validate requirements document format and completeness"""
        validation_results = {
            "valid": True,
            "issues": [],
            "suggestions": []
        }
        
        # Check for basic structure
        if "# Requirements Document" not in requirements:
            validation_results["issues"].append("Missing main title '# Requirements Document'")
            validation_results["valid"] = False
        
        if "## Introduction" not in requirements:
            validation_results["issues"].append("Missing Introduction section")
            validation_results["valid"] = False
        
        if "## Requirements" not in requirements:
            validation_results["issues"].append("Missing Requirements section")
            validation_results["valid"] = False
        
        # Check for user stories
        if "**User Story:**" not in requirements:
            validation_results["issues"].append("No user stories found")
            validation_results["valid"] = False
        
        # Check for EARS format
        ears_keywords = ["WHEN", "THEN", "SHALL", "IF"]
        if not any(keyword in requirements for keyword in ears_keywords):
            validation_results["issues"].append("No EARS format criteria found (WHEN/THEN/SHALL/IF)")
            validation_results["valid"] = False
        
        # Suggestions for improvement
        if requirements.count("### Requirement") < 3:
            validation_results["suggestions"].append("Consider adding more detailed requirements (found less than 3)")
        
        if "edge case" not in requirements.lower():
            validation_results["suggestions"].append("Consider adding edge case handling requirements")
        
        if "error" not in requirements.lower():
            validation_results["suggestions"].append("Consider adding error handling requirements")
        
        return validation_results
    
    def export_spec_documents(self) -> Dict[str, str]:
        """Export all specification documents"""
        documents = {}
        
        if st.session_state.get("requirements_doc"):
            documents["requirements.md"] = st.session_state.requirements_doc
        
        if st.session_state.get("design_doc"):
            documents["design.md"] = st.session_state.design_doc
        
        if st.session_state.get("task_list"):
            # Tasks are now already in markdown format
            tasks = st.session_state.task_list
            if isinstance(tasks, str) and tasks.strip():
                documents["tasks.md"] = tasks
            elif isinstance(tasks, list) and tasks:
                # Fallback for old JSON format if it still exists
                tasks_md = "# Implementation Tasks\n\n"
                for i, task in enumerate(tasks, 1):
                    if isinstance(task, dict):
                        tasks_md += f"## {i}. {task.get('title', 'Untitled Task')}\n\n"
                        tasks_md += f"**Description:** {task.get('description', 'No description')}\n\n"
                        tasks_md += f"**Priority:** {task.get('priority', 'medium')}\n\n"
                        tasks_md += f"**Estimated Hours:** {task.get('estimated_hours', 'TBD')}\n\n"
                        
                        if task.get('requirements_refs'):
                            tasks_md += f"**Requirements:** {', '.join(task['requirements_refs'])}\n\n"
                        
                        if task.get('acceptance_criteria'):
                            tasks_md += "**Acceptance Criteria:**\n"
                            for criteria in task['acceptance_criteria']:
                                tasks_md += f"- {criteria}\n"
                            tasks_md += "\n"
                        
                        tasks_md += "---\n\n"
                
                documents["tasks.md"] = tasks_md
        
        return documents