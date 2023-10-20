from tkinter import *
from tkinter.messagebox import showinfo
import datetime as dt

FONT = ('Courier', 14)
BIG_FONT = ('Courier', 22, 'bold')
TIME_LIMIT = 60  # in seconds


class App:
    def __init__(self):
        self.window = Tk()

        self.user_words_count = 0
        self.user_chars_count = 0
        self.start_time = None
        self.seconds_remaining = TIME_LIMIT
        self.timer = None

        self.cpm = StringVar(value='?')
        self.wpm = StringVar(value='?')
        self.time = StringVar(value=f'{self.seconds_remaining}')
        self.user_text = StringVar()
        self.text_canvas = None

        with open('./words.txt') as words_file:
            self.test_words = words_file.read().split()

        self.user_text.trace_add("write", self.update)
        self.ui()

    def reset(self):
        self.user_words_count = 0
        self.user_chars_count = 0
        self.start_time = None
        self.seconds_remaining = TIME_LIMIT
        if self.timer:
            self.window.after_cancel(self.timer)

        self.cpm.set('?')
        self.wpm.set('?')
        self.time.set(f'{self.seconds_remaining}')
        self.user_text.set('')

        self.text_canvas.tag_remove('current', 0.0, END)
        self.text_canvas.tag_remove('correct', 0.0, END)
        self.text_canvas.tag_remove('incorrect', 0.0, END)
        self.text_canvas.tag_add('current', '0.0 wordstart', '0.0 wordend')

    def show_result(self):
        # Notify user of score
        showinfo(title='Your Results!', message=f'Here are your results:\n'
                                                f'CPM={self.cpm.get()}\n'
                                                f'WPM={self.wpm.get()}\n'
                                                f'Good job!')
        # Reset the system
        self.reset()

    def countdown(self):
        if self.seconds_remaining > 0:
            # Timer did not expire
            self.timer = self.window.after(1000, self.countdown)
            self.seconds_remaining -= 1
            self.time.set(f'{self.seconds_remaining}')
        else:
            # Timer expired, so show the results
            self.show_result()

    def update_counters(self):
        # Register how much time passed
        time_passed: dt.timedelta = dt.datetime.now() - self.start_time
        secs_passed = time_passed.seconds

        if secs_passed > 0:
            # Update the counters
            cpm = str(round(self.user_chars_count / (secs_passed / 60)))
            wpm = str(round(self.user_words_count / (secs_passed / 60)))
            self.cpm.set(cpm)
            self.wpm.set(wpm)

    def update(self, *args):
        if not self.user_text.get():
            # User did not enter any text, it is a misfire
            return

        if not self.start_time:
            # Start time not set, so start it and init the counter
            self.start_time = dt.datetime.now()
            self.timer = self.window.after(1000, self.countdown)

        if self.user_text.get()[-1] == ' ':
            # Check if the word is correct
            entered_word = self.user_text.get().strip()
            try:
                correct_word = self.text_canvas.get('current.first', 'current.last')
            except TclError:
                # User ran out of words
                self.show_result()
            else:
                if entered_word == correct_word:
                    # Add correct tag
                    self.text_canvas.tag_add('correct', 'current.first', 'current.last')

                    # Add the word to the correct words
                    self.user_words_count += 1

                    # Increment the number of chars
                    self.user_chars_count += len(entered_word)
                else:
                    # Add incorrect tag
                    self.text_canvas.tag_add('incorrect', 'current.first', 'current.last')

                # Update cpm and wpm counters
                self.update_counters()

                # Move the "current" tag to the next word
                idx = self.text_canvas.index('current.last + 1 chars')
                self.text_canvas.tag_remove('current', 'current.first', 'current.last')
                self.text_canvas.tag_add('current', f'{idx}', f'{idx} wordend')

                # Clear the user entry
                self.user_text.set('')

    def ui(self):
        # Update the window attributes
        self.window.title('Typing Speed Test')
        self.window.config(pady=10, padx=10)

        # Create widgets
        cpm_label = Label(text='CPM:', font=FONT)
        cpm_entry = Entry(textvariable=self.cpm, justify='center', state='disabled')
        wpm_label = Label(text='WPM:', font=FONT)
        wpm_entry = Entry(textvariable=self.wpm, justify='center', state='disabled')
        time_label = Label(text='Time Left:', font=FONT)
        time_entry = Entry(textvariable=self.time, justify='center', state='disabled')
        reset_button = Button(text='Reset', command=self.reset)
        user_entry = Entry(justify='center', textvariable=self.user_text, font=BIG_FONT)

        # Create the words canvas
        self.text_canvas = Text(width=60, height=20, bg='#191919',
                                font=BIG_FONT, padx=30, pady=30,
                                wrap=WORD)
        self.text_canvas.insert(index=1.1, chars=' '.join(self.test_words))
        self.text_canvas.config(state='disabled')

        # Create the tags
        self.text_canvas.tag_config('correct', foreground='#4287f5')
        self.text_canvas.tag_config('incorrect', foreground='#f55a42')
        self.text_canvas.tag_config('current', background='#ad42f5')

        # Move the "current" tag to the first word
        self.text_canvas.tag_add('current', '0.0 wordstart', '0.0 wordend')

        # Create the grid
        cpm_label.grid(row=0, column=0, sticky='news', padx=3)
        cpm_entry.grid(row=0, column=1, sticky='news', padx=3)
        wpm_label.grid(row=0, column=2, sticky='news', padx=3)
        wpm_entry.grid(row=0, column=3, sticky='news', padx=3)
        time_label.grid(row=0, column=4, sticky='news', padx=3)
        time_entry.grid(row=0, column=5, sticky='news', padx=3)
        reset_button.grid(row=0, column=6, sticky='news', padx=3)
        self.text_canvas.grid(row=1, column=0, columnspan=7, sticky='news')
        user_entry.grid(row=2, column=0, columnspan=7, sticky='news')

        # Start the events loop
        self.window.mainloop()


if __name__ == '__main__':
    app = App()
