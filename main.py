import os
import base64
import argparse
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

load_dotenv()

console = Console()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

SYSTEM_PROMPT = '''
You are Figma-to-UX Review, an extremely critical AI design review agent.

Act as:
- Senior Product Designer
- UX Lead
- Design Systems Specialist
- Accessibility Expert
- CRO Consultant

Your job is to critique digital interfaces with professional product judgment.

Be direct, senior, specific and actionable.
Explain WHY something is wrong.
Prioritize usability, accessibility, conversion and scalability.

Use this exact structure:

# Executive Summary

# UX Issues

## Issue

### Problem
### User Impact
### Severity
### Recommendation
### Improved Example

# Accessibility Findings

# UI Consistency Problems

# Conversion Opportunities

# Priority Fixes

# Quick Wins

# Suggested Next Iteration

Also include:
- UX Score /100
- UI Score /100
- Accessibility Score /100
- Conversion Score /100
- Design System Score /100
- Overall Product Experience Score /100
'''


def encode_image(image_path: str) -> str:
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def review_image(image_path: str, context: str = '') -> str:
    image_base64 = encode_image(image_path)

    response = client.responses.create(
        model='gpt-5.5',
        input=[
            {
                'role': 'system',
                'content': SYSTEM_PROMPT
            },
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'input_text',
                        'text': f'''Analyze this interface screenshot.\n\nContext:\n{context}\n\nBe extremely critical and actionable.'''
                    },
                    {
                        'type': 'input_image',
                        'image_url': f'data:image/png;base64,{image_base64}'
                    }
                ]
            }
        ]
    )

    return response.output_text


def review_text(description: str) -> str:
    response = client.responses.create(
        model='gpt-5.5',
        input=[
            {
                'role': 'system',
                'content': SYSTEM_PROMPT
            },
            {
                'role': 'user',
                'content': f'''Analyze this interface based on this visual description:\n\n{description}\n\nBe extremely critical and professional.'''
            }
        ]
    )

    return response.output_text


def save_review(content: str, name: str = 'ux_review.md'):
    Path('reviews').mkdir(exist_ok=True)
    output_path = Path('reviews') / name
    output_path.write_text(content, encoding='utf-8')
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Figma-to-UX Review AI Agent')
    parser.add_argument('--image', help='Path to screenshot or Figma export')
    parser.add_argument('--text', help='Visual description of the interface')
    parser.add_argument('--context', default='', help='Extra business/product context')
    parser.add_argument('--out', default='ux_review.md', help='Output markdown file')

    args = parser.parse_args()

    if not args.image and not args.text:
        console.print('[red]You must provide --image or --text[/red]')
        return

    console.print(Panel('Running AI UX Review...', title='Figma-to-UX Review'))

    if args.image:
        result = review_image(args.image, args.context)
    else:
        result = review_text(args.text)

    output_path = save_review(result, args.out)

    console.print(result)
    console.print(f'\n[green]Review saved to:[/green] {output_path}')


if __name__ == '__main__':
    main()
