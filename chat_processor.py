from datetime import datetime
from utils import sanitize_filename
from parser import get_conversation, TOOL_HANDLERS, format_web_search, format_code_execution



def analyze_conversation(mapping):
    roles = {}
    tool_types = {}
    assistant_json = 0

    def traverse(node_id, visited=None):
        nonlocal assistant_json
        if visited is None:
            visited = set()
        if node_id in visited:
            return
        visited.add(node_id)
        node = mapping[node_id]
        if node.get('message'):
            role = node['message']['author']['role']
            roles[role] = roles.get(role, 0) + 1
            if role == "tool":
                for part in node['message']['content'].get('parts', []):
                    if isinstance(part, dict):
                        tool_name = part.get('name', 'unknown')
                        tool_types[tool_name] = tool_types.get(tool_name, 0) + 1
            elif role == "assistant":
                for part in node['message']['content'].get('parts', []):
                    if isinstance(part, dict) and "query" in part:
                        assistant_json += 1
        for child_id in node.get('children', []):
            traverse(child_id, visited)

    root_node_id = next(node_id for node_id, node in mapping.items() if node.get('parent') is None)
    traverse(root_node_id)
    return roles, tool_types, assistant_json

def extract_metadata(item, conversation_text, is_voice):
    title = sanitize_filename(item.get("title"))
    created_dt = datetime.fromtimestamp(item["create_time"])
    created_str = created_dt.strftime("%Y-%m-%d %H:%M")
    update_time = item.get("update_time")
    modified_str = "" if not update_time else datetime.fromtimestamp(update_time).strftime("%Y-%m-%d %H:%M")
    
    word_count = len(conversation_text.split())
    char_count = len(conversation_text)
    user_posts = conversation_text.count("## 👤 user")
    assistant_posts = conversation_text.count("## 🤖 assistant")
    tool_posts = conversation_text.count("## 🛠️ tool")
    status = "bad" if "🚫" in title else ""
    voice_mode = "voice" if is_voice else ""
    
    return {
        "title": title,
        "created": created_str,
        "modified": modified_str,
        "word_count": word_count,
        "char_count": char_count,
        "user_posts": user_posts,
        "assistant_posts": assistant_posts,
        "tool_posts": tool_posts,
        "status": status,
        "voice": voice_mode
    }

def format_yaml_header(metadata):
    voice_line = f"voice_mode: {str('true' if metadata['voice'] else 'false')}\n" if metadata['voice'] else ""
    return (
        "---\n"
        f"title: \"{metadata['title']}\"\n"
        f"created: \"{metadata['created']}\"\n"
        f"modified: \"{metadata['modified']}\"\n"
        f"word_count: {metadata['word_count']}\n"
        f"char_count: {metadata['char_count']}\n"
        f"user_posts: {metadata['user_posts']}\n"
        f"assistant_posts: {metadata['assistant_posts']}\n"
        f"tool_posts: {metadata['tool_posts']}\n"
        f"status: \"{metadata['status']}\"\n"
        f"{voice_line}"
        "---\n\n"
    )