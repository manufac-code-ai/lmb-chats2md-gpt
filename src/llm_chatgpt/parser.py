#!/usr/bin/env python3
from datetime import datetime

def format_web_search(content):
    if isinstance(content, dict) and "homeResults" in content:
        return "\n".join([f"- {r.get('title', 'No Title')}" for r in content["homeResults"]])
    return str(content)

def format_code_execution(content):
    return f"```python\n{content}\n```" if isinstance(content, str) else str(content)

TOOL_HANDLERS = {
    "web_search": format_web_search,
    "code_interpreter": format_code_execution,
    # Add others later
}

def get_conversation(node_id, mapping, conversation_list, last_author=None, visited=None, is_voice=None):
    """
    Extract conversation content from the conversation mapping.
    
    Args:
        node_id (str): The ID of the current node.
        mapping (dict): The conversation mapping from the JSON data.
        conversation_list (list): The list to append conversation parts to.
        last_author (str, optional): The last author role. Defaults to None.
        visited (set, optional): Set of visited node IDs. Defaults to None.
        is_voice (list, optional): Single-item list indicating if voice mode is detected. Defaults to None.
        
    Returns:
        bool: True if voice mode is detected, False otherwise.
    """
    if visited is None:
        visited = set()
    if is_voice is None:
        is_voice = [False]
    processed_tool = False
    if node_id in visited:
        return is_voice[0], processed_tool
    visited.add(node_id)

    node = mapping[node_id]
    if node.get('message') and 'content' in node['message'] and 'parts' in node['message']['content']:
        content_parts = node['message']['content']['parts']
        parts_text = []
        timestamp = None

        author_role = node['message']['author']['role']

        for part in content_parts:
            if isinstance(part, str):
                parts_text.append(part)
            elif isinstance(part, dict):
                text = part.get('text')
                if text:
                    parts_text.append(text)
                elif author_role == "tool":
                    tool_name = part.get('name')
                    tool_content = part.get('content')
                    if tool_name and tool_content:
                        if tool_name in TOOL_HANDLERS:
                            formatted_output = TOOL_HANDLERS[tool_name](tool_content)
                            parts_text.append(formatted_output)
                            processed_tool = True
                        else:
                            parts_text.append(f"[Tool: {tool_name} output - see original data]")
                    else:
                        parts_text.append("[Unknown tool output]")
                
                if part.get('content_type') in ['audio_transcription', 'real_time_user_audio_video_asset_pointer']:
                    is_voice[0] = True
                
                meta_dict = part.get('metadata')
                if not meta_dict or not isinstance(meta_dict, dict):
                    audio_asset = part.get('audio_asset_pointer')
                    if audio_asset and isinstance(audio_asset, dict):
                        meta_dict = audio_asset.get('metadata')
                
                if meta_dict and isinstance(meta_dict, dict) and 'start' in meta_dict and 'end' in meta_dict:
                    start = meta_dict.get('start')
                    end = meta_dict.get('end')
                    if start is not None and end is not None:
                        duration = int(end - start)
                        minutes, seconds = divmod(duration, 60)
                        timestamp = f"[{minutes}:{seconds:02d}]"

        if parts_text:
            text = ''.join(parts_text)
            if timestamp and is_voice[0]:
                text += f" {timestamp}"
            emoji_map = {"user": "👤 ", "assistant": "🤖 ", "tool": "🛠️ "}
            emoji = emoji_map.get(author_role, "")
            if author_role != "system" and author_role != last_author:
                conversation_list.append(f"## {emoji}{author_role}\n{text}")
            elif author_role != "system":
                conversation_list.append(f"{emoji}{text}")
            last_author = author_role

    for child_id in node.get('children', []):
        child_voice, child_processed = get_conversation(child_id, mapping, conversation_list, last_author, visited, is_voice)
        processed_tool = processed_tool or child_processed

    return is_voice[0], processed_tool