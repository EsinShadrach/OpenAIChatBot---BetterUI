import customtkinter
import openai as oa
from datetime import datetime as dt
import json

# TODO: CREATE A SESSION CACHE DICTIONARY LIKE
"""
session_cache = {}
session_cache["question"] = "response"
"""


class App(customtkinter.CTk):
    def __init__(self, fg_color=("#dddddd", "#04050c")):
        super().__init__(fg_color)
        # * ++++++++ Creating app structure And Variables ++++++++ * #
        # TODO: session dictionary here
        self.bgTuple: tuple = ("white", "#02030f")
        self.borderColorTuple = ("#ffd69b", "#222b3f")
        self.session = {}
        self.title("Chat Bot..?")
        self.geometry("600x500")
        # * ++++++++ Creating app structure Endblock ++++++++ * #
        userData = open('user.json')
        self.apiKey = (json.loads(userData.read())["Api-key"])
        oa.api_key = self.apiKey
        self.UserFrame = customtkinter.CTkFrame(
            self, fg_color=self.bgTuple, corner_radius=0, border_width=2, border_color=self.borderColorTuple
        )
        self.OpenAIKeyEntry = customtkinter.CTkEntry(
            self.UserFrame, border_width=2,
            border_color=self.borderColorTuple,
            fg_color="transparent", placeholder_text="Enter Open AI API Key",
            width=500
        )
        self.button = customtkinter.CTkButton(
            self.UserFrame, text=">", command=self._apiKeyCallBack
        )
        self.UserFrame.pack(fill="both", expand=False, pady=10)
        self.UserFrame.grid_rowconfigure(0, weight=1)  # configure grid system
        self.UserFrame.grid_columnconfigure((0, 1), weight=1)
        self.OpenAIKeyEntry.grid(
            row=1, column=0, padx=10, pady=10, sticky="ew"
        )
        self.button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # * ++++++++ Creating Input Frame ++++++++ * #
        self.entryFrame = customtkinter.CTkFrame(
            self, fg_color=self.bgTuple,
            corner_radius=0, border_width=2,
            border_color=self.borderColorTuple
        )
        self.entryTextBox = customtkinter.CTkTextbox(
            self.entryFrame, fg_color="transparent"
        )
        self.entryButton = customtkinter.CTkButton(
            self.entryFrame, text=">>", font=("system-ui", 20, "bold"),
            command=self._callback
        )
        # * ++++++++ Creating Input Frame Endblock ++++++++ * #

        # * ++++++++ Packing Items ++++++++ * #
        self.entryFrame.pack(fill="both", expand=False)
        self.entryTextBox.pack(fill="both", expand=True, padx=10, pady=20)
        self.entryButton.pack(expand=True)
        # * ++++++++ Packing Items Endblock ++++++++ * #

        # * ++++++++ Creating Output Frame ++++++++ * #
        self.outputFrame = customtkinter.CTkScrollableFrame(
            self, fg_color=self.bgTuple,
            border_width=2, border_color=self.borderColorTuple,
            label_text="Hello"
        )
        self.outputTextBox = customtkinter.CTkTextbox(
            self.outputFrame, fg_color="transparent"
        )
        # * ++++++++ Creating Output Frame Endblock ++++++++ * #

        # * ++++++++ Packing Items ++++++++ * #
        self.outputFrame.pack(fill="both", expand=False, padx=10, pady=20)
        self.outputTextBox.pack(expand=True, fill="both")
        # * ++++++++ Packing Items Endblock ++++++++ * #

    def _apiKeyCallBack(self, writeTo=True):
        with open("user.json", "w+") as f:
            if writeTo:
                api_key = self.OpenAIKeyEntry.get()
                UserDict = {"Api-key": api_key}
                data = json.dumps(UserDict, indent=4)
                f.write(data)
            else:
                return f.read()

    def _callback(self):
        Query = self.entryTextBox.get('0.0', 'end')
        TextBoxEntry = self.entryTextBox.get('0.0', 'end').strip()
        if TextBoxEntry != '':
            if Query in self.session.keys():  # returns true
                question_return = self.session.get(Query)
                self.outputTextBox.insert('0.0', question_return)
            else:
                self._to_openAI(Query)
            self.outputFrame.configure(
                label_text="I hope this helps! Let me know if you have any other questions.")
        else:
            self.outputFrame.configure(label_text="Enter an input")

    def _to_openAI(self, data: str):
        prompt = f"{data}"
        language_map = {
            'python': 'py',
            'javascript': 'js',
            'js': 'js',
            'html': 'html',
            'css': 'css',
            'cpp': 'cpp',
            'c++': 'cpp',
        }
        language = [
            key for key in language_map.keys() if key in prompt.lower()
        ]
        file_extension = language_map[language[0]] if language else 'txt'
        # TODO: Check if prompt is not in session dictionary here
        try:
            response = oa.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.5,
                max_tokens=2000,
            )

        except Exception as e:
            self._handle_exception(e)

        response_list = [
            j for i in response.get("choices") for j in i.get("text")
        ]
        question_return = f'{"".join(response_list).strip()}\n'
        self._write_to_file(
            InputData=question_return,
            file_extension=file_extension,
            ErrorOccurred=False
        )
        self._storeData(prompt, question_return)
        self.outputTextBox.insert('0.0', question_return)

    def _handle_exception(self, e, file_extension='txt'):
        self.outputFrame.configure(label_text="An Error Occurred")
        ActualError = f"[{dt.now()}] - {e}.\n"
        self.outputTextBox.insert('0.0', ActualError)
        self._write_to_file(
            InputData=ActualError,
            file_extension=file_extension, ErrorOccurred=True
        )

    def _write_to_file(self, InputData: str, file_extension: str, ErrorOccurred: bool = True) -> None:
        with open('CrashLog.txt', 'a') as has_errors, open('gpt.txt', 'a') as no_errors:
            if ErrorOccurred:  # * If there is no error
                has_errors.write(f"{InputData}\n")
                has_errors.close()
            else:
                no_errors.write(f"{InputData}\n")
                no_errors.close()

    def _storeData(self, key, value):
        self.session[key] = value
        with open('sessionData.json', 'w+') as db:
            data = self.session
            data = json.dumps(data, indent=4)
            db.write(data)


if __name__ == "__main__":
    app = App()
    app.mainloop()
