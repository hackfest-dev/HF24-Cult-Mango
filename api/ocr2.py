from transformers import DonutProcessor

def josnconv(gen_text):

    processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")
    return processor.token2json(gen_text)


