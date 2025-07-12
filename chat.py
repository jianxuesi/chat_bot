import google.generativeai as genai
import json

GOOGLE_API_KEY= "AIzaSyCEzH3-dchkGXkRq7b0oZMaksZLMkjem8A"
genai.configure(api_key=GOOGLE_API_KEY)
model_name = 'gemini-2.0-flash-exp' #@param ['gemini-1.5-flash', "gemini-1.5-flash-8b","gemini-1.5-flash-002","gemini-1.5-pro-002","gemini-2.0-flash-exp"]
model = genai.GenerativeModel(model_name)
prompt = "You are a japanese chatbot. Not matter which languarge user is typing. Always return in Japansese. Here is the user \nnew user input: \n{}  \n\nFormer conversation as Context: \n{}"
prompt2 = "You are a japanese languarge partner. Not matter which languarge user is saying. Always return in Japansese only. No need to include romaji or pronunciation in the return. Please chat like a japanese girl. If you want to know more about the user, feel free to ask questions if needed. Here is the user \nnew user input: \n{}  \n\nFormer conversation as Context: \n{} \n\nSummary of the user: \n{}"
context = ""
user_input = ""
summary_prompt = "You are a japanese languarge partner. Not matter which languarge user is saying. Always return in Japansese only. You just had a conversation with the user. Pleaes extract user's information from it. Here is the speech: \n{} \n\nFormer summary of the user: \n{}"

def chat_LLM(user_input, context, summary):
  request = prompt2.format(user_input, context, summary)
  response = model.generate_content(
    request
  )
  generated_text = response.text
  return generated_text

def get_summary(user_input, summary):
	request = summary_prompt.format(user_input, summary)
	response = model.generate_content(request)
	return response.text


if __name__ == '__main__':
	context = ""
	user_input = ""
	summary = ""
	try:
		with open('sample.json', 'r') as openfile:
			json_object = json.load(openfile)
			if "summary" in json_object:
				summary = json_object["summary"]
	except:
		pass
	while user_input != "bye":
		user_input = input()
		generated_text = chat_LLM(user_input, context, summary)
		context += "user:" + user_input + "\n agent(self):" + generated_text + "\n"
		print("Chatbot Speech:", generated_text)

	summary = get_summary(context, summary)
	print("summary: ", summary)

	json_object = json.dumps({"summary": summary})

	# Writing to sample.json
	with open("sample.json", "w") as outfile:
		outfile.write(json_object)



