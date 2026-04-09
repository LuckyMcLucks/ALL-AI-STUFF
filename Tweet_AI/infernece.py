

import torch
import torch.nn as nn
import torch
from transformers import BertTokenizer, BertModel, pipeline
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


pretrained_weights = "bert-base-cased"
tokenizer = BertTokenizer.from_pretrained(pretrained_weights)
model = BertModel.from_pretrained(pretrained_weights)

nlp = pipeline("feature-extraction", tokenizer=tokenizer, model=model,device=0)

def tokenizeTweets(text):
  
  
  vectorized_docs = []
  # Encode text
  vec = np.array(nlp(text[:512]))
  meanVec = vec.reshape((vec.shape[1], vec.shape[2])).mean(axis=0)
  vectorized_docs.append(meanVec)
  return np.array(vectorized_docs)

class LSTMWithHN(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, num_layers=1, output_dim=1, dropout_prob=0.2):
        super().__init__()
        self.num_layers =num_layers
        self.hidden_dim = hidden_dim
        self.lstm = nn.GRU(input_dim, hidden_dim, num_layers, batch_first=True)
        self.dropout = nn.Dropout(dropout_prob)
        self.layer_100 = nn.Linear(hidden_dim + 16 ,100)
        self.dropout2= nn.Dropout(dropout_prob)
        self.fc = nn.Linear(100, output_dim)
        
        self.meta = nn.Linear(4, 4)
        self.meta_2 = nn.Linear(4, 16)

    def forward(self, x, meta_features, hc=None):
        batch_size = x.size(0)  #
        # hc = (h0, c0) if provided, otherwise defaults to zeros
        if hc== (None,None):
            h0 = torch.zeros(self.num_layers, batch_size, self.hidden_dim, device=x.device)
            c0 = torch.zeros(self.num_layers, batch_size, self.hidden_dim, device=x.device)
            hc = (h0, c0)
        out = self.lstm(x, hc)
        
        # Use hn of the last layer
        last_hidden = out[0] # shape: [batch_size, hidden_dim]
        last_hidden = self.dropout(last_hidden)
        
        meta_features = self.meta(meta_features)
        meta_features = self.meta_2(meta_features)
        
        last_hidden = torch.cat([last_hidden, meta_features], dim=1)
        last_hidden = self.layer_100(last_hidden)
        last_hidden = self.dropout2(last_hidden)
        
        out = self.fc(last_hidden)
        
        # Return updated hidden and cell states for potential next batch
        return out
    
    
model = LSTMWithHN(input_dim=768, hidden_dim=128, num_layers=1, output_dim=1)
model.load_state_dict(torch.load("metaGRU_model_weights.pth",weights_only=True))
model.eval()

from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()
origins = [
    "http://localhost:3000",  # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, OPTIONS, etc.
    allow_headers=["*"],
)
class TweetRequest(BaseModel):
    text: str
    meta_features: list[float]

@app.post("/predict")
def predict(request: TweetRequest):
    text = request.text
    meta = request.meta_features

    vectorized_text = tokenizeTweets(text)

    input_tensor = torch.tensor(vectorized_text, dtype=torch.float32)
    meta_tensor = torch.tensor([meta], dtype=torch.float32)

    with torch.no_grad():
        output = model(input_tensor, meta_tensor)
        conf = torch.sigmoid(output).item()
        pred = (conf >= 0.3)
        print(pred , conf)
        

    return {"prediction": str(pred), "confidence": conf}

# if __name__ == "__main__":
#     # Example usage
    
#     text = "This is an example tweet for testing."
#     vectorized_text = tokenizeTweets(text)
#     meta_features = torch.tensor([[0.5, 0.2, 0.1, 0.3]])  # Example meta features
#     output = model(torch.tensor(vectorized_text, dtype=torch.float32), meta_features)
#     conf = torch.sigmoid(output).item()
#     preds = (conf >= 0.3)
#     print(preds , conf)