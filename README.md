# Final-Year-Project

# Sent Scrape

A tool made for primarily quantifying user opinions on PC hardware to help aid purchasing decisions  
Two Sentiment Analysis approaches are used (Lexicon-Based And Pretrained Model)  
There are currently 4 platforms available for opinion retrieval each with their own tweakable parameters, implemeneted via Webscraping and APIs  

![image](https://user-images.githubusercontent.com/77795437/198416850-d4e41cf2-feaa-4e04-8aa3-01b79f45fa7c.png)

# Understanding Scoring

## VADER (Lexicon-Based)
![image](https://user-images.githubusercontent.com/77795437/201168914-93dc8fc9-4c7a-4f17-a658-68ad3e83495f.png)
## ROBERTA (Pretrained Model)
If an NVIDIA GPU Is present, the CUDA device will be used to speed up model inference

![image](https://user-images.githubusercontent.com/77795437/201169078-3e8129cd-2471-4070-8d3d-069dc80e8edf.png)

# Platforms 

Platforms implemented, are typical sites we may use to find opinions on a product before making a purchase

![image](https://user-images.githubusercontent.com/77795437/198411318-c1740020-091f-47d6-8e1f-acb6beea739c.png)

Reddit Form Example

![image](https://user-images.githubusercontent.com/77795437/198413769-c0ae72e7-1477-4ee2-a8ab-05540600294f.png)

# Assessment

On completion of analysis, the user will receive an assessment based on the collected dataset which includes an interactable graph. The user may use the legends to enable/disable plotted lines and the graph will auto rescale

## VADER Assessment
![image](https://user-images.githubusercontent.com/77795437/198414330-42e52491-8edd-4354-ac22-0e785f3572ac.png)

## ROBERT Assessment
![image](https://user-images.githubusercontent.com/77795437/198414000-93e466b3-2a5f-48ee-ab18-f5efbc302573.png)

## Example Data Set Snapshot

Post Search, the collected data sets are reviewable and are displayed via a fully ineractable table which allows sorting of comment scores based on column

![image](https://user-images.githubusercontent.com/77795437/198414439-546e751d-d3c8-44fc-a9d0-bff5599ac22e.png)

# Search History 

Here, user's can review an identical summary page for past searches and view their collected data sets. An option to delete a past searches is also available 

![image](https://user-images.githubusercontent.com/77795437/198905697-cd929056-03ab-469b-bf46-ecf4a7b54d03.png)

![image](https://user-images.githubusercontent.com/77795437/198905713-b03e0258-9a65-40c3-8a31-bffcfa3bc234.png)

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
- Corresponding Chromedriver for your Google Chrome version from https://chromedriver.chromium.org/downloads

# Built With

- Python selenium/PRAW for scraping
- Python eel library for GUI communication with python scripts
- Python NLTK for VADER 
- Python Transformers for pretrained model
- Chartjs for graphing
