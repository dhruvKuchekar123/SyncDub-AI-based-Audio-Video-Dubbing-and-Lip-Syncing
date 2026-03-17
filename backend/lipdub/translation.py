from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

class Translator:
    def __init__(self, model_name='facebook/m2m100_418M', src_lang='hi', tgt_lang='mr'):
        print('Loading translator:', model_name)
        self.tokenizer = M2M100Tokenizer.from_pretrained(model_name)
        self.model = M2M100ForConditionalGeneration.from_pretrained(model_name)
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

    def translate(self, text):
        # NOTE: for long texts, consider chunking
        self.tokenizer.src_lang = self.src_lang
        encoded = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=1024)
        generated = self.model.generate(**encoded, forced_bos_token_id=self.tokenizer.get_lang_id(self.tgt_lang), max_length=1024)
        out = self.tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
        return out
