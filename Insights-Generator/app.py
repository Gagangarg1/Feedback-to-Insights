import google.generativeai as genai
import pandas as pd
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import pipeline
import pickle
from typing import List, Dict
import matplotlib.pyplot as plt
from kneed import KneeLocator
import json
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from gensim import corpora
from gensim.models import LdaModel
from transformers import pipeline


nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('vader_lexicon')
nltk.download('stopwords')


genai.configure(api_key='KEEP the key here')
model = genai.GenerativeModel('gemini-pro')


def preprocess_text(text):
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if not word in stop_words]
    return tokens

def generate_tags(idea):
    prompt = f"""
    Generate 3 relevant tags or keywords for the following idea. 
    Provide only the tags, separated by commas, without any additional text.
    
    Idea: {idea}
    
    Tags:
    """
    response = model.generate_content(prompt)
    tags = response.text.strip().split(',')
    return [tag.strip() for tag in tags]

def create_tag_dict(feedback_dict):
    tag_dict = {}
    for id, content in feedback_dict.items():
        tags = generate_tags(content)
        for tag in tags:
            if tag not in tag_dict:
                tag_dict[tag] = [id]
            else:
                tag_dict[tag].append(id)
    with open('tag_dict.pkl', 'wb') as file:
        pickle.dump(tag_dict, file)
    return tag_dict

def cluster_tags(tags):
    prompt = f"""
    Task: Analyze the following list of tags and group them into meaningful clusters.

    Tags: {', '.join(tags)}

    Instructions:
    1. Examine the tags and identify common themes or categories.
    2. Create 6 clusters based on these themes. The number of clusters should depend on the diversity of the tags.
    3. Assign a short, descriptive name to each cluster.
    4. Allocate each tag to the most appropriate cluster. Each tag should be in only one cluster.
    5. Ensure that no tags are left unclustered.

    Provide your response in the following format:
    {{
        "cluster_name1": ["tag1", "tag2", "tag3"],
        "cluster_name2": ["tag4", "tag5"],
        ...
    }}

    Your response must be valid JSON and nothing else. Do not include any explanations, prefixes, or additional text.
    """
    
    response = model.generate_content(prompt)
    response_text = response.text
    cleaned_response = re.sub(r'^[\s\S]*?(?=\{)', '', response_text.strip())
    cleaned_response = re.sub(r'}[\s\S]*$', '}', cleaned_response)
    try:
        # Parse the JSON response
        clustered_tags = json.loads(cleaned_response)
        with open('clustered_tags.pkl', 'wb') as file:
            pickle.dump(clustered_tags, file)
        return clustered_tags
    except json.JSONDecodeError:
        print("Error: Unable to parse JSON response from Gemini.")
        return {}

def create_clustered_feedback_dict(loaded_cluster_dict, loaded_tag_dict):
    clustered_feedback_dict = {}
    for cluster_name, tags in loaded_cluster_dict.items():
        for tag in tags:
            if tag in loaded_tag_dict:
                for idea_id in loaded_tag_dict[tag]:
                    content = feedback_dict[idea_id]
                    if cluster_name not in clustered_feedback_dict:
                        clustered_feedback_dict[cluster_name] = [[content], 1]
                    elif content in clustered_feedback_dict[cluster_name][0]:
                        clustered_feedback_dict[cluster_name][1] += 1
                    else:
                        clustered_feedback_dict[cluster_name][0].append(content)
                        clustered_feedback_dict[cluster_name][1] += 1

    with open('clustered_feedback_dict.pkl', 'wb') as file:
        pickle.dump(clustered_feedback_dict, file)
    return clustered_feedback_dict

def generate_clustered_summary(feedback_clusters):
    cluster_summary_dict = {}
    for cluster_name, feedbacks in feedback_clusters.items():
        prompt = f"""
        Analyze the following group of user feedback tagged as "{cluster_name}":

        {feedbacks[0]}

        Summarize all the feedbacks taken together as one within the given tag. Give more priority to:
        1. Creativity: Innovative solutions or approaches.
        2. Relevance: Ensure insights directly address the feedback themes.
        3. Uniqueness: Highlight any standout or unexpected ideas.
        4. Actionability: Specific, implementable actions.

        Provide a concise summary of the feedback in one paragraph max 50 words.

        """

        response = model.generate_content(prompt)
        cluster_summary_dict[cluster_name] = response.text

    with open('clustered_summary_dict.pkl', 'wb') as file:
        pickle.dump(cluster_summary_dict, file)

    return cluster_summary_dict

def generate_category_summary(feedback_clusters):
    category_summary_dict = {}
    for category, feedbacks in feedback_clusters.items():
        prompt = f"""
        Analyze the following group of user feedback tagged as "{category}":

        {feedbacks[0]}

        Summarize all the feedbacks taken together as one within the given tag. Give more priority to:
        1. Creativity: Innovative solutions or approaches.
        2. Relevance: Ensure insights directly address the feedback themes.
        3. Uniqueness: Highlight any standout or unexpected ideas.
        4. Actionability: Specific, implementable actions.

        Provide a concise summary of the feedback in one paragraph max 50 words.

        """

        response = model.generate_content(prompt)
        category_summary_dict[category] = response.text

    with open('category_summary_dict.pkl', 'wb') as file:
        pickle.dump(category_summary_dict, file)

    return category_summary_dict


def generate_summary(cluster_summary_dict):
    prompt = f"""
    Analyze the following list of user feedbacks:

    {cluster_summary_dict.values()}

    Summarize all the feedbacks taken together as one. Give more priority to:
    1. Creativity: Innovative solutions or approaches.
    2. Relevance: Ensure insights directly address the feedback themes.
    3. Uniqueness: Highlight any standout or unexpected ideas.
    4. Actionability: Specific, implementable actions.

    Provide a concise summary of the feedback in one paragraph max 50 words.

    """

    response = model.generate_content(prompt)
    return response.text

def generate_summary2(category_summary_dict):
    prompt = f"""
    Analyze the following list of user feedbacks:

    {category_summary_dict.values()}

    Summarize all the feedbacks taken together as one. Give more priority to:
    1. Creativity: Innovative solutions or approaches.
    2. Relevance: Ensure insights directly address the feedback themes.
    3. Uniqueness: Highlight any standout or unexpected ideas.
    4. Actionability: Specific, implementable actions.

    Provide a concise summary of the feedback in one paragraph max 50 words.

    """

    response = model.generate_content(prompt)
    return response.text


def generate_insights(feedback_clusters):
    insights = {}
    for cluster_name, feedbacks in feedback_clusters.items():
        prompt = f"""
        Analyze the following group of user feedback tagged as "{cluster_name}":

        {feedbacks[0]}

        Generate 3 key actionable insights based on this feedback in 10 words max. Focus on:
        1. Creativity: Propose innovative solutions or approaches.
        2. Relevance: Ensure insights directly address the feedback themes.
        3. Uniqueness: Highlight any standout or unexpected ideas.
        4. Actionability: Suggest specific, implementable actions.

        Format your response as a bulleted list of concise, actionable insights.
        """

        response = model.generate_content(prompt)
        insights[cluster_name] = response.text

    return insights

def generate_insights2(feedback_category):
    insights = {}
    for category, feedbacks in feedback_category.items():
        prompt = f"""
        Analyze the following group of user feedback tagged as "{category}":

        {feedbacks[0]}

        Generate 2 key actionable insights based on this feedback in 10 words max. Focus on:
        1. Creativity: Propose innovative solutions or approaches.
        2. Relevance: Ensure insights directly address the feedback themes.
        3. Uniqueness: Highlight any standout or unexpected ideas.
        4. Actionability: Suggest specific, implementable actions.

        Your response must be a list of comma-separated actionable insights. Do not include any prefixes, or additional text.
        """

        response = model.generate_content(prompt)
        insights[category] = response.text

    return insights

def model_topics(preprocessed_reviews):
    dictionary = corpora.Dictionary(preprocessed_reviews)
    corpus = [dictionary.doc2bow(review) for review in preprocessed_reviews]
    lda_model = LdaModel(corpus, num_topics=4, id2word=dictionary, passes=15)
    topics = lda_model.print_topics(num_words=4)
    return topics

def generate_meaningful_topics(lda_topics):
    prompt = "Given the following LDA topic model results, please generate meaningful topic labels:\n\n"
    for topic_id, topic in lda_topics:
        prompt += f"Topic {topic_id}: {topic}\n"
    prompt += "\nPlease provide a concise label for each topic."
    prompt += "\nThe response should be a list of topic labels, separated by commas."

    # Generate response from Gemini
    response = model.generate_content(prompt)
    
    return response.text

def classify_feedback(feedback, categories):
    prompt = f"""
    Classify the following user feedback into one of these categories: {', '.join(categories)}
    
    Feedback: "{feedback}"
    
    Return only the category name, nothing else.
    """

    response = model.generate_content(prompt)
    
    # Extract and return the classification
    return response.text.strip()

def generate_categorized_feedback_dict(feedback_dict, categories):
    categorized_feedback_dict = {}
    for feedback in feedback_dict.values():
        category = classify_feedback(feedback, categories)
        if category not in categorized_feedback_dict:
            categorized_feedback_dict[category] = [[feedback], 1]
        else:
            categorized_feedback_dict[category][0].append(feedback)
            categorized_feedback_dict[category][1] += 1

    with open('categorized_feedback_dict.pkl', 'wb') as file:
        pickle.dump(categorized_feedback_dict, file)
    return categorized_feedback_dict

def getoutput():
    df = pd.read_csv('feedback.csv')
    feedback_dict = dict(zip(df['id'], df['content']))
    genai.configure(api_key='AIzaSyAYRceDdvwYLOW5yIjcm6A36LqQVHULBwA')
    model = genai.GenerativeModel('gemini-pro')
    preprocessed_reviews = [preprocess_text(review) for review in df['content']]
    topics = model_topics(preprocessed_reviews)
    meaningful_topics = generate_meaningful_topics(topics)
    categorized_feedback_dict = generate_categorized_feedback_dict(feedback_dict, meaningful_topics.split(','))
    with open('categorized_feedback_dict.pkl', 'rb') as file:
        loaded_categorized_feedback_dict = pickle.load(file)
    insights2 = generate_insights2(loaded_categorized_feedback_dict)
    return insights2



if __name__ == "__main__": 
    

    df = pd.read_csv('feedback.csv')
    feedback_dict = dict(zip(df['id'], df['content']))
    genai.configure(api_key='AIzaSyAYRceDdvwYLOW5yIjcm6A36LqQVHULBwA')
    model = genai.GenerativeModel('gemini-pro')

    #1
    #tag_dict = create_tag_dict(feedback_dict)
    #with open('tag_dict.pkl', 'rb') as file:
    #    loaded_tag_dict = pickle.load(file)
    #print(loaded_tag_dict)

    #2
    #clustered_tags = cluster_tags(loaded_tag_dict.keys()) 
    #with open('clustered_tags.pkl', 'rb') as file:
    #    loaded_cluster_dict = pickle.load(file)
    #print(loaded_cluster_dict)

    #3
    #clustered_feedback_dict = create_clustered_feedback_dict(loaded_cluster_dict, loaded_tag_dict)
    #with open('clustered_feedback_dict.pkl', 'rb') as file:
    #    loaded_clustered_feedback_dict = pickle.load(file)
    #print(loaded_clustered_feedback_dict)

    #4
    #cluster_summary_dict = generate_clustered_summary(loaded_clustered_feedback_dict)
    #with open('clustered_summary_dict.pkl', 'rb') as file:
    #    loaded_cluster_summary_dict = pickle.load(file)
    #print(loaded_cluster_summary_dict)

    #5
    #final_summary = generate_summary(loaded_cluster_summary_dict)
    #print(final_summary)

    preprocessed_reviews = [preprocess_text(review) for review in df['content']]
    
    #6
    #insights = generate_insights(loaded_clustered_feedback_dict)
    #print(insights)

    #7
    topics = model_topics(preprocessed_reviews)
    meaningful_topics = generate_meaningful_topics(topics)

    #8
    categorized_feedback_dict = generate_categorized_feedback_dict(feedback_dict, meaningful_topics.split(','))
    with open('categorized_feedback_dict.pkl', 'rb') as file:
        loaded_categorized_feedback_dict = pickle.load(file)
    #print(loaded_categorized_feedback_dict)

    #9
    #category_summary_dict = generate_category_summary(loaded_categorized_feedback_dict)
    #with open('category_summary_dict.pkl', 'rb') as file:
    #    loaded_category_summary_dict = pickle.load(file)
    #print(loaded_category_summary_dict)

    #10
    #final_summary2 = generate_summary2(loaded_categorized_feedback_dict)
    #print(final_summary2)

    #11
    insights2 = generate_insights2(loaded_categorized_feedback_dict)
    print(insights2)
    




    





