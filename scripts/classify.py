import os
import torch
import sys
import json
from transformers import AutoModelForQuestionAnswering, AutoModelForCausalLM, AutoTokenizer, pipeline
from datasets import Dataset


DEVICE = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

QA_MODEL = 'deepset/roberta-base-squad2'
MAX_LENGTH = 800
THRESHOLD_SCORE = 0.7

def extract_predictions(ocr_text):

    question='When will the war end?'

    nlp = pipeline('question-answering', model=QA_MODEL, tokenizer=QA_MODEL, device=0)

    chunks = nlp.tokenizer(
        question,
        ocr_text,
        max_length=MAX_LENGTH,
        truncation="only_second",           # only to truncate context
        stride=70,                          # no of overlapping tokens  between concecute context pieces
        return_overflowing_tokens=True,     #to let tokenizer know we want overflow tokens
    )

    def gen():
        for chunk in chunks['input_ids']:
            yield {
                'question': question, 
                'context': nlp.tokenizer.decode(chunk)
            }

    dataset = Dataset.from_generator(gen)
    answers = nlp(dataset)
    for answer in answers:
        if answer['score'] > THRESHOLD_SCORE:
            print(answer['answer'])


def load_text(file_path):
    with open(file_path, "r") as file:
        return file.read()


# Main function to extract predictions and print results
def main():
    # Load the OCR text from a file (replace with your actual OCR file path)
    data_dir = None
    if len(sys.argv) == 2:
        data_dir = sys.argv[1]

    if not data_dir:
        sys.exit(1)

    for file in os.listdir(data_dir):
        print(file)
        ocr_text = load_text(data_dir + os.sep + file)
        extract_predictions(ocr_text)


if __name__ == "__main__":
    main()
