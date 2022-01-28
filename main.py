import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import re
from messages import *
from services.bdWrapper import *
from datetime import datetime


def get_city_id(text):
    cities = get_all_cities()
    for city in cities:
        city_id, city_name, city_regex = city
        if text.lower() == city_name.lower() or re.match(rf'{city_regex.lower()}', text.lower()) is not None:
            return city_id
    return None


def check_flight_availability(departure_city_id, destination_city_id):
    return len(get_flights(departure_city_id, destination_city_id)) != 0


def get_suitable_flights(date, departure_city_id, destination_city_id):
    flights = get_flights(departure_city_id, destination_city_id)
    upcoming_flights = []
    now_date = datetime.strptime(str(datetime.now()).split()[0], "%Y-%m-%d")
    for flight in flights:
        flight_date = datetime.strptime(flight[2], "%d-%m-%Y")
        if flight_date >= now_date:
            upcoming_flights.append(flight)
    if len(upcoming_flights) <= 5:
        return upcoming_flights
    need_date = datetime.strptime(date, "%d-%m-%Y")
    suitable_flights = []
    for index in range(len(upcoming_flights)):
        flight = upcoming_flights[index]
        flight_date = datetime.strptime(flight[2], "%d-%m-%Y")
        if flight_date >= need_date:
            try:
                suitable_flights.append(upcoming_flights[index - 2])
            except Exception:
                suitable_flights.append(upcoming_flights[index + 3])
            try:
                suitable_flights.append(upcoming_flights[index - 1])
            except Exception:
                suitable_flights.append(upcoming_flights[index + 4])
            suitable_flights.append(upcoming_flights[index])
            try:
                suitable_flights.append(upcoming_flights[index + 1])
            except Exception:
                suitable_flights.insert(0, upcoming_flights[index - 3])
            try:
                suitable_flights.append(upcoming_flights[index + 2])
            except Exception:
                suitable_flights.insert(0, upcoming_flights[index - 4])
            return sorted(suitable_flights)
    return []


class Bot:
    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def send(self, user_id, message=None, attachment=None, keyboard=None):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0,
                                         "attachment": attachment, 'keyboard': keyboard})

    def run(self):
        for event in self.long_poller.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                text, user_id = event.object["text"], event.object["from_id"]
                print(text, user_id)
                if not check_user_presence(user_id):
                    create_user(user_id)
                if text == HELP_COMMAND:
                    set_status(user_id, "")
                    set_data(user_id, "")
                    self.send(user_id, HELP_MESSAGE)
                elif text == TICKET_COMMAND:
                    set_status(user_id, "ENTER_DEPARTURE_CITY")
                    set_data(user_id, "")
                    self.send(user_id, ENTER_DEPARTURE_CITY)
                else:
                    status, data = get_status(user_id), get_data(user_id)
                    if status == "ENTER_DEPARTURE_CITY":
                        city_id = get_city_id(text)
                        if city_id is not None:
                            set_data(user_id, str(city_id))
                            set_status(user_id, "ENTER_DESTINATION_CITY")
                            self.send(user_id, ENTER_DESTINATION_CITY)
                        else:
                            msg = INVALID_DEPARTURE_CITY
                            msg = msg.replace("<CITY_NAME>", str(get_city_name(get_last_flight()[3])))
                            self.send(user_id, msg)
                        continue
                    elif status == "ENTER_DESTINATION_CITY":
                        city_id = get_city_id(text)
                        if city_id is not None:
                            if check_flight_availability(data, city_id):
                                set_data(user_id, f'{data};{str(city_id)}')
                                set_status(user_id, "ENTER_DATE")
                                self.send(user_id, ENTER_DATE)
                            else:
                                set_status(user_id, "")
                                set_data(user_id, "")
                                self.send(user_id, NO_FLIGHTS_IN_CITIES)
                        else:
                            msg = INVALID_DESTINATION_CITY
                            msg = msg.replace("<CITY_NAME>", str(get_city_name(get_last_flight()[4])))
                            self.send(user_id, msg)
                        continue
                    elif status == "ENTER_DATE":
                        departure_city_id, destination_city_id = get_data(user_id).split(";")
                        try:
                            flights = get_suitable_flights(text, departure_city_id, destination_city_id)
                        except ValueError:
                            self.send(user_id, ENTER_DATE)
                            continue
                        text = FLIGHTS_LIST
                        for flight in flights:
                            text += f"{flight[1]} - {flight[2]} - {get_city_name(departure_city_id)} - {get_city_name(destination_city_id)}\n"
                        self.send(user_id, text)
                        self.send(user_id, ENTER_FLIGHT_NUMBER)
                        set_status(user_id, "ENTER_FLIGHT_NUMBER")
                        set_data(user_id, "")
                        continue
                    elif status == "ENTER_FLIGHT_NUMBER":
                        if check_flight_presence(text):
                            set_status(user_id, "ENTER_SEATS_NUMBER")
                            set_data(user_id, text)
                            self.send(user_id, ENTER_SEATS_NUMBER)
                            continue
                        else:
                            self.send(user_id, ENTER_FLIGHT_NUMBER)
                            continue
                    elif status == "ENTER_SEATS_NUMBER":
                        try:
                            seats_amount = int(text)
                        except Exception:
                            self.send(user_id, ENTER_SEATS_NUMBER)
                            continue
                        if seats_amount not in list(range(1, 6)):
                            self.send(user_id, ENTER_SEATS_NUMBER)
                            continue
                        set_status(user_id, "ENTER_COMMENT")
                        set_data(user_id, f"{data};{seats_amount}")
                        self.send(user_id, ENTER_COMMENT)
                        continue
                    elif status == "ENTER_COMMENT":
                        flight_number, amount_seats = get_data(user_id).split(";")
                        flight = get_flight(flight_number)
                        msg = CHECK_DATA
                        msg += f"Номер рейса: {flight[1]}\n"
                        msg += f"Дата рейса: {flight[2]}\n"
                        msg += f"Город отправления: {get_city_name(flight[3])}\n"
                        msg += f"Город прибытия: {get_city_name(flight[4])}\n"
                        msg += f"Кол-во сидений: {amount_seats}\n"
                        msg += f"Комментарий: {text}\n"
                        msg += f"\n{DATA_IS_CORRECT}"
                        self.send(user_id, msg)
                        set_status(user_id, "CHECK_DATA")
                        set_data(user_id, f"{data};{text}")
                        continue
                    elif status == "CHECK_DATA":
                        if text.lower() == "да":
                            self.send(user_id, ENTER_PHONE_NUMBER)
                            set_status(user_id, "ENTER_PHONE_NUMBER")
                        elif text.lower() == "нет":
                            set_status(user_id, "")
                            set_data(user_id, "")
                            self.send(user_id, GENERATE_NEW_ORDER_TEXT)
                        else:
                            self.send(user_id, DATA_IS_CORRECT)
                        continue
                    elif status == "ENTER_PHONE_NUMBER":
                        set_status(user_id, "")
                        set_data(user_id, "")
                        self.send(user_id, END_ORDER)
                    else:
                        self.send(user_id, HELP_MESSAGE)


if __name__ == "__main__":
    bot = Bot(VK_GROUP_ID, VK_TOKEN_BOT)
    bot.run()
