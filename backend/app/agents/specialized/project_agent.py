from app.agents.base_agent import BaseAgent


class ProjectAgent(BaseAgent):
    name = "project_agent"
    description = "Supports project planning, sprints, tasks, risks and delivery tracking."
    capabilities = ["sprint planning", "task breakdown", "risk analysis", "project status"]
    supported_tools = ["project_search", "calendar", "task_manager"]
    prompt_template = """You are the Enterprise Project Management Agent.
Turn goals into practical tasks, owners, dependencies, risks and acceptance criteria.
Use supplied project data as the source of truth and clearly label assumptions."""

    @classmethod
    def can_handle(cls, message: str) -> bool:
        keywords = ("project", "sprint", "task", "jira", "roadmap", "deadline", "milestone", "risk")
        text = message.lower()
        return any(word in text for word in keywords)
