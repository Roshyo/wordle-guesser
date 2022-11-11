import words_list
import letters_frequency_list
import operator
import copy
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def main():
    words = words_list.get_words_list()

    mode = 'local'  # 'local' will guess a random word in list. 'online' will play on the web browser

    if 'local' == mode:
        word_to_guess = random.choice(words)
        print('The word to guess is: ' + word_to_guess)
    else:
        driver = webdriver.Chrome()
        driver.get('https://www.nytimes.com/games/wordle/index.html')
        time.sleep(1)
        assert 'Wordle' in driver.title
        cookie_consent_reject = driver.find_element(By.ID, 'pz-gdpr-btn-reject')
        cookie_consent_reject.click()
        modal_close_button = driver.find_element(By.CLASS_NAME, 'Modal-module_closeIcon__b4z74')
        modal_close_button.click()
        time.sleep(10)
        keys_buttons_selector = '.Key-module_key__Rv-Vp'
        enter_button = driver.find_element(By.CSS_SELECTOR, '%s[data-key="↵"]' % keys_buttons_selector)

    for i in range(1, 7):
        guess = get_guess(words)
        print('Guess is: ' + guess)

        if 'online' == mode:
            for letter in guess:
                css_selector = '%s[data-key="%s"]' % (keys_buttons_selector, letter)
                key_button = driver.find_element(By.CSS_SELECTOR, css_selector)
                key_button.click()

            enter_button.click()
            time.sleep(2)

            comparison = decode_hints(i, driver)
        else:
            comparison = compare_words(word_to_guess, guess)

        print('Comparison: ' + comparison)
        if 'vvvvv' == comparison:
            print('the word is: ' + guess)
            break

        words = remove_ineligible_words(guess, comparison, words)

    input()


def get_guess(words):
    words_score = {}
    for word in words:
        word_score = get_word_score(word)
        words_score[word] = word_score

    words_score = dict(sorted(words_score.items(), key=operator.itemgetter(1), reverse=True))
    return next(iter(words_score))


def get_word_score(word):
    letters_frequency = letters_frequency_list.get_letters_frequency()
    word_value = 0
    used_letters = []
    for letter in word:
        if letter in used_letters:
            letter_weight = 1
        else:
            letter_weight = letters_frequency[letter]
        word_value += letter_weight
        used_letters.append(letter)

    return round(word_value, 3)


def compare_words(original, guess):
    result = ''
    for key in range(len(guess)):
        guessed_letter = guess[key]
        if guessed_letter in original:
            if original[key] == guessed_letter:
                result += 'v'
            else:
                result += 'o'
        else:
            result += 'x'

    return result


def remove_ineligible_words(guess, result, words):
    new_words = []
    for key in range(len(result)):
        letter_hint = result[key]
        guessed_letter = guess[key]
        new_words = copy.copy(words)
        for word in words:
            if letter_hint == 'v':
                if word[key] != guessed_letter:
                    new_words.remove(word)
            if letter_hint == 'x':
                if guessed_letter in word:
                    new_words.remove(word)
            if letter_hint == 'o':
                if guessed_letter not in word:
                    new_words.remove(word)
                if word[key] == guessed_letter:
                    new_words.remove(word)
        words = new_words
    return new_words


def decode_hints(attempt_number, driver):
    result = ''
    for i in range(1, 6):
        letter = driver.find_element(
            By.CSS_SELECTOR,
            '.Row-module_row__dEHfN:nth-of-type(%d) > div:nth-of-type(%d) > .Tile-module_tile__3ayIZ' % (attempt_number, i)
        )
        if 'correct' == letter.get_attribute('data-state'):
            result += 'v'
        elif 'present' == letter.get_attribute('data-state'):
            result += 'o'
        else:
            result += 'x'

    return result


main()
