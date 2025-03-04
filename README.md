# Sent-Scrape-Final_Year_Project

# Sent Scrape
```
A tool made for primarily quantifying opinions on topics and products to provide insights.  

Two Sentiment Analysis approaches are used (Lexicon-Based[VADER] And Pretrained Model[RoBERTa])  

There are currently 4 platforms available each with their own tweakable parameters, data Is gathered using Webscraping and APIs  
```

![image](https://user-images.githubusercontent.com/77795437/201180710-688bd3ae-bc17-4424-b624-1ed042fc6e7f.png)

# Understanding Scoring

## VADER (Lexicon-Based)
![image](https://user-images.githubusercontent.com/77795437/201168914-93dc8fc9-4c7a-4f17-a658-68ad3e83495f.png)
## ROBERTA (Pretrained Model)

```
If an NVIDIA GPU Is present, the CUDA device will be used to speed up model inference
```

![image](https://user-images.githubusercontent.com/77795437/201169078-3e8129cd-2471-4070-8d3d-069dc80e8edf.png)

# Platforms 
```
Platforms implemented, are popular sites we may use to find opinions on different things.
```

![image](https://user-images.githubusercontent.com/77795437/201179855-24270606-0b0b-4776-ab38-edb85d51061c.png)

# Form example

## Reddit 

![Form](https://github.com/Jonathan9168/Final-Year-Project/assets/77795437/c51a81d1-0d2e-4a9c-9e1e-8a2bd6b1e36f)

# Assessment
```
On completion of analysis, the user will receive an assessment based on the collected dataset which includes an interactable graph. 

The user may use the legends to enable/disable plotted lines and the graph will auto rescale.
```
## VADER Assessment
![image](https://user-images.githubusercontent.com/77795437/232574473-efbc2fd5-5d4d-46c7-a67c-dccf9d46b213.png)

## RoBERTa Assessment
![image](https://user-images.githubusercontent.com/77795437/232574144-9a71df9f-6f0e-4c89-89d4-994b87633b58.png)

## Example Data Set Snapshots
```
After a search, the collected data sets are reviewable and are displayed via a fully ineractable table which allows sorting of comment scores based on column.
```
![image](https://user-images.githubusercontent.com/77795437/201177609-8ddc76ce-3d57-420a-a473-c4ddf874a339.png)

![image](https://user-images.githubusercontent.com/77795437/201179369-68d74e4a-a7b2-4e22-86a3-469a7d3010e0.png)

# Search History 
```
Here, user's can view summary pages and datasets for past searches, view frequent word pairs, delete searches and compare searches.
Additionaly the user can import searches into the localc directory and edit them.
```
![image](https://user-images.githubusercontent.com/77795437/235301306-ca15f75d-fd17-486b-8b52-9fc914ba998f.png)

# Search Comparison
```
A user can compare the scoring of their searches by using available checkboxes for searches analysed using the same Sentiment Analysis methodology.  

This in turn allows for the comparison of a single search on a paticular platform overtime; cross platform comparisons of the same or different search term; or even a way to just individually see scoring for a search on seperate graphs.
```
## Example VADER Comparisons

### Scatter

![image](https://user-images.githubusercontent.com/77795437/231744381-3866c4dc-1912-487d-9977-833f0e6954e1.png)

### Radar

![image](https://user-images.githubusercontent.com/77795437/198905383-44118c29-0813-4ae7-8c87-9435268abbfa.png)

## Example ROBERT Comparisons

### Scatter

![image](https://user-images.githubusercontent.com/77795437/231744998-5b47425c-4957-484c-93d5-7f57cc5e5f84.png)

### Radar

![image](https://user-images.githubusercontent.com/77795437/231745242-f7d753ad-f8da-438a-81e6-8a026dc855bb.png)

# Comparisons In Action 

<p align="center">
    <img src="https://user-images.githubusercontent.com/77795437/239709588-edda8efd-1535-4988-a9fd-771e77440924.gif" width="100%">
</p>

# Consecutive word pairs
```
This allows the user to view the top 15 frequent word pairs to gain a quick insight into the dataset.
```
![image](https://user-images.githubusercontent.com/77795437/235326595-3489fb10-9148-455c-a0ff-e02abc57576f.png)

# Requirements
```
- Google Chrome
```
# Built With
```
- Python selenium/PRAW for scraping
- Python's eel library for front-end GUI communication with back-end python scripts
- Python's NLTK for VADER 
- Python's Transformers for RoBERTa model
- Chartjs for graphing
```
