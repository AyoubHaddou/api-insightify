from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForCausalLM
import torch, string, random
import pandas as pd 

tokenizer = AutoTokenizer.from_pretrained("DAMO-NLP-SG/zero-shot-classify-SSTuning-base")
model_zero_shot = AutoModelForSequenceClassification.from_pretrained("DAMO-NLP-SG/zero-shot-classify-SSTuning-base")

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
list_ABC = [x for x in string.ascii_uppercase]

def check_text(model, text, list_label, shuffle=False): 
    list_label = [x for x in list_label]
    list_label_new = list_label + [tokenizer.pad_token]* (20 - len(list_label))
    if shuffle: 
        random.shuffle(list_label_new)
    s_option = ' '.join(['('+list_ABC[i]+') '+list_label_new[i] for i in range(len(list_label_new))])
    text = f'{s_option} {tokenizer.sep_token} {text}'

    model.to(device).eval()
    encoding = tokenizer([text],truncation=True, max_length=512,return_tensors='pt')
    item = {key: val.to(device) for key, val in encoding.items()}
    logits = model(**item).logits
    
    logits = logits if shuffle else logits[:,0:len(list_label)]
    probs = torch.nn.functional.softmax(logits, dim = -1).tolist()
    predictions = torch.argmax(logits, dim=-1).item() 
    probabilities = [round(x,5) for x in probs[0]]

    return pd.Series([list_label_new[predictions], round(probabilities[predictions]*100,2)])