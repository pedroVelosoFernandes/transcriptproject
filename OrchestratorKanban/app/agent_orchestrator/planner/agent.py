from strands import Agent
from model.load import load_model
from planner.prompts import PLANNER_SYSTEM_PROMPT
from planner.models import KanbanPlan


def create_planner_tool():
    planner = Agent(
        name="planner",
        description=(
            "Analyzes a meeting transcript against the current Kanban board state "
            "and returns a structured action plan of issues to create, update, or move. "
            "Input must contain <TRANSCRIPT> and <BOARD_STATE> XML sections."
        ),
        model=load_model(),
        system_prompt=PLANNER_SYSTEM_PROMPT,
        tools=[],
        structured_output_model=KanbanPlan,
        callback_handler=None,
    )
    return planner.as_tool()
