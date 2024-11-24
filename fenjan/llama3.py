from fenjan.linkedin import extractions
import requests, json, os

temp_folder = os.path.join(os.path.dirname(__file__), "temp")
results_path = os.path.join(temp_folder, "results.html")

# Check the number of chunks and their lengths
# for i, section in enumerate(search_results):
# print(f"Chunk {i+1} Length: {len(section)} characters")
# for section in sections:
#     print(f"Chunk Length: {len(section)} characters")

# Set the LLaMA API URL and headers
ollama_url = "http://localhost:11434/api/generate"
headers = {"Content-Type": "application/json"}

payload_extract_template = {
    "model": "llama3",
    "temperature": 0.3,
    "stream": False,
    "max_tokens": 512,
}

results = []
# The only criterion to distingush position description sections from each other is that every position description section is embeded inside a HTML division element in the following HTML content, with the class="update-components-text relative update-components-update-v2__commentary".
# Consider the division elements texts as one position description section.

# for i, section in enumerate(sections):
# for keyword in extractions:
# for i, section in enumerate(keyword):

for keyword, sections in extractions.items():
    for i, section in enumerate(sections):
        print(f"Keyword: {keyword}, Section {i}: {section}")
        # return

        payload_extract = payload_extract_template.copy()
        payload_extract[
            "prompt"
        ] = f"""
            This section is part of several linkedin position search results, in HTML format, for some keywords, like phd, llm, etc (Hereafter is called their_keywords). Each set of search results' sections for their_keyword is separated from others by a section as a divider and information, with the below pattern:
            divider section : <h2> These are realted positions for their_keyword: </h2>🔎🔗: <a href=https://www.linkedin.com/search/results/content/?keywords=%22phd%22&origin=GLOBAL_SEARCH_HEADER&sid=L.U&sortBy=%22date_posted%22>search url for their_keyword</a><br>
            Keep the divider intact in place to maintain the overall structue and return it as it is.
            Organize the section (other than divider) in this way:
            Produce a title and a summary from {section["position_text"]}. Even if there is no clear title, please use the first sentence as the title.
            

            Structure the extracted data as a string like the following format (for non-divider sections):

                "Title": "First sentence or inferred title of the position description section"
                "Summary": "position description section"
                "HTML Content": {section["position_html_block"]}

            For divider section ({section["position_html_block"]}) return it as it is.

            """

        # Make the POST request with the AI API
        response_extract = requests.post(
            ollama_url, headers=headers, data=json.dumps(payload_extract)
        )

        response_text = response_extract.text

        # Parse the response as JSON
        # response_json = json.loads(response_text)

        # Extract the 'response' part
        # extracted_response = response_json.get("response", "No response found.")
        """
        extracted_response = response_text.get("response", "No response found.")

        # Print the extracted response
        print(f"Response for the section {i}: \n{extracted_response}")

        if response_extract.status_code == 200:
            results.append(extracted_response)
        """
        print(f"Response for the section {i}: \n{response_text}")

        if response_extract.status_code == 200:
            results.append(response_text)

        # Combine results from ?
        # combined_results = [item for sublist in results for item in sublist]

        # Assuming combined_results is a list of dictionaries from each chunk
        # for i, result in enumerate(combined_results):
        # print(f"result {i}: {result}")

        # structured_data = response_extract.json().get("choices")[0].get("text")
        # structured_data = json.loads(structured_data)

        # Ensure structured_data contains the extracted information from step 1
        # Payload for formatting the structured data

    # print(f"results:\n {results}")
    # Check if the file exists
    # if not os.path.exists(results_path):
    #     print(f"File {results_path} does not exist.")
    # else:
    # write the file contents
    with open(results_path, "w", encoding="utf-8") as f:
        f.write(str(results))
