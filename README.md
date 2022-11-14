# Final-Year-Project

# Sent Scrape

A tool made for primarily quantifying user opinions on PC hardware to help aid purchasing decisions  
Two Sentiment Analysis approaches are used (Lexicon-Based And Pretrained Model)  
There are currently 4 platforms available for opinion retrieval each with their own tweakable parameters, implemeneted via Webscraping and APIs  

![image](https://user-images.githubusercontent.com/77795437/201180710-688bd3ae-bc17-4424-b624-1ed042fc6e7f.png)

# Understanding Scoring

## VADER (Lexicon-Based)
![image](https://user-images.githubusercontent.com/77795437/201168914-93dc8fc9-4c7a-4f17-a658-68ad3e83495f.png)
## ROBERTA (Pretrained Model)
If an NVIDIA GPU Is present, the CUDA device will be used to speed up model inference

![image](https://user-images.githubusercontent.com/77795437/201169078-3e8129cd-2471-4070-8d3d-069dc80e8edf.png)

# Platforms 

Platforms implemented, are typical sites we may use to find opinions on a product before making a purchase

![image](https://user-images.githubusercontent.com/77795437/201179855-24270606-0b0b-4776-ab38-edb85d51061c.png)

# Form examples

## Reddit 

![image](https://user-images.githubusercontent.com/77795437/201761781-26d767ea-7156-410f-ac49-ce2fa3102be2.png)

## YouTube

![image](https://user-images.githubusercontent.com/77795437/201761977-de559c19-9985-42b1-bf6b-7a7b740a8fbe.png)

# Assessment

On completion of analysis, the user will receive an assessment based on the collected dataset which includes an interactable graph. The user may use the legends to enable/disable plotted lines and the graph will auto rescale

## VADER Assessment
![image](https://user-images.githubusercontent.com/77795437/198414330-42e52491-8edd-4354-ac22-0e785f3572ac.png)

## ROBERT Assessment
![image](https://user-images.githubusercontent.com/77795437/198414000-93e466b3-2a5f-48ee-ab18-f5efbc302573.png)

## Example Data Set Snapshot

Post search, the collected data sets are reviewable and are displayed via a fully ineractable table which allows sorting of comment scores based on column

![image](https://user-images.githubusercontent.com/77795437/201177609-8ddc76ce-3d57-420a-a473-c4ddf874a339.png)

![image](https://user-images.githubusercontent.com/77795437/201179369-68d74e4a-a7b2-4e22-86a3-469a7d3010e0.png)

# Search History 

Here, user's can review an identical summary page for past searches and view their collected data sets. An option to delete a past searches is also available 

![image](https://user-images.githubusercontent.com/77795437/201176643-bfbea628-81d4-4a88-86d7-d541bd67659a.png)

![image](https://user-images.githubusercontent.com/77795437/201176853-0159b3c9-b595-4d10-801b-cdc25b7a9e99.png)

# Search Comparison

A user can compare the scoring of their searches by using available checkboxes for searches analysed using the same Sentiment Analysis methodology.  

This in turn allows for the comparison of a single product on a paticular platform overtime; cross platform comparisons of the same or different products; or even a way to just individually see scoring for a search on seperate graphs

## Example VADER Comparisons

### Line

![image](https://user-images.githubusercontent.com/77795437/198415764-b59b1672-4b97-4c6f-ba41-73fb69ae5bbc.png)

### Radar

![image](https://user-images.githubusercontent.com/77795437/198905383-44118c29-0813-4ae7-8c87-9435268abbfa.png)

## Example ROBERT Comparisons

### Line

![image](https://user-images.githubusercontent.com/77795437/198416024-40cf9486-f89b-4c7b-b37a-6f7c99f6f211.png)

### Radar

![image](https://user-images.githubusercontent.com/77795437/198905603-df38fc7d-533c-4202-ae2a-86c146441fdb.png)

# Requirements
- Google Chrome

# Built With

- Python selenium/PRAW for scraping
- Python eel library for GUI communication with python scripts
- Python NLTK for VADER 
- Python Transformers for pretrained model
- Chartjs for graphing
