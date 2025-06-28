from transformers import pipeline

# Load summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

text = """
Artificial intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving.
"""

print("Original text:")
print(text)

result = summarizer(text, max_length=50, min_length=20, do_sample=False)
summary = result[0]['summary_text']

print("\nSummary:")
print(summary)
