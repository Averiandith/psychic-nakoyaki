#############################################################################################
# Victor (28/6/2022)
#
# obtain your own app keys (api_key, api_secret, token): https://trello.com/app-key
# py-trello docs (wrapper API): https://py-trello-dev.readthedocs.io/en/latest/trello.html#module-trello.base
# Trello REST API docs: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/
#############################################################################################

from trello import TrelloClient, Card, Board, Member
from datetime import datetime
from typing import Union
import pandas as pd
import requests
import json


class Client:
    def __init__(self, api_key: str, api_secret: str, token: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.token = token

    def create_client(self) -> TrelloClient:
        """
        Function to return a TrelloClient API
        """
        return TrelloClient(
            api_key = self.api_key,
            api_secret = self.api_secret,
            token = self.token
        )

class Board:
    def __init__(self, client: TrelloClient) -> None:
        self.client = client

    def list_all_boards(self) -> None:
        """
        Function to get list of boards & their respective ids
        """
        all_boards = self.client.list_boards()
        for board in all_boards:
            print(f'Board Name: {board.name}, Board ID: {board.id}')

    def get_ad_hoc_board(self) -> Board:
        """
        Function to get my team's ad-hoc board
        """
        return self.client.list_boards()[0]

class Member:
    def __init__(self, board: Board) -> None:
        self.board = board
    
    def get_all_members_from_board(self) -> list:
        return self.board.all_members()

    def bind_member_id_and_name(self) -> dict:
        """
        Function to return a dictionary of member id and names in a board
        """
        member_list = self.get_all_members_from_board()
        member_dict = {}
        for member in member_list:
            member_dict[str(member.id)] = [str(member.full_name)][0]

        return member_dict

class Helper:
    @staticmethod
    def pretty_format_list_movements(test_card: Card) -> list:
        """
        Function to pretty format list movements and return a list of tuples 
        """
        movement_collection_list = []
        list_movements = test_card.list_movements()

        for movement in reversed(list_movements):
            source = "".join(filter(str.isalpha, movement['source']['name']))
            destination = "".join(filter(str.isalpha, movement['destination']['name']))
            datetime = movement['datetime'].strftime('%d/%m/%Y, %H:%M:%S')

            movement_collection_list.append({'source': source, 'destination': destination, 'datetime': datetime})

        return movement_collection_list

    @staticmethod
    def convert_member_id_to_name(member_id_list: list, member_dict: dict) -> str:
        """
        Function that reads in member id & name dictionary key pair and convert a card's member id(s) to name
        """
        if len(member_id_list) == 0:
            return '' 

        member_name_str = '' 
        for member_id in member_id_list:
            if len(member_name_str) > 0:
                member_name_str += f", {member_dict[member_id]}"
            else:
                member_name_str = str(member_dict[member_id])

        return member_name_str

    @staticmethod
    def process_description(description: str) -> Union[dict, str]:
        """
        Function to process description gibberish into meaningful columns.
        """
        if description.find("###") != -1:
            description_basic = description.split("Attachment", 1)
            description_basic = description_basic[0]

            data_arr = description_basic.split("###")
            for i in range(len(data_arr)):
                data_arr[i] = data_arr[i].replace("\n", "")
                data_arr[i] = data_arr[i].strip()

            # Using list comprehension to perform empty string removal
            data_arr = [string for string in data_arr if string]

            # Split the data into even and odd fashion to process into key value pair
            keys = []
            values = []
            for i in range(len(data_arr)):
                if i % 2 == 0:
                    keys.append(data_arr[i])
                else:
                    values.append(data_arr[i])
            
            data_dict = {}
            for i in range(len(keys)):
                data_dict[keys[i]] = values[i]

            print(data_dict)
            return data_dict 
        else:
            print(description)
            return description

    @staticmethod
    def get_card_label(card_id: str) -> str:
        """
        Because PyTrello is not able to extract card label, call Trello's API directly
        """
        url = f"https://api.trello.com/1/cards/{card_id}"

        headers = {
           "Accept": "application/json"
        }

        query = {
           'key': 'Get Your Own Key',
           'token': 'Get Your Own Key'
        }

        response = requests.request(
           "GET",
           url,
           headers = headers,
           params = query
        )

        # Use this to output data of the card in json format
        # json.dumps(json.loads(response.text), sort_keys = True, indent = 4, separators = (",", ": ")))

        data = json.loads(response.text)
        labels = data['labels']

        final_string = ""
        if len(labels) > 0:
            for i in range(len(labels)):
                if i == 0:
                    final_string += f"{labels[i]['name']}"
                else:
                    final_string += f", {labels[i]['name']}"
        else:
            final_string = "N/A"

        return final_string

    @staticmethod
    def export_cards_to_csv(board: Board, member: Member) -> None:
        """
        Function to export all cards from given board to csv (archive cards included)
        """    
        result = []
        member_dict = member.bind_member_id_and_name()

        for list in board.list_lists():
            for card in list.list_cards():

                created_date = card.created_date
                current_list = "".join(filter(str.isalpha, list.name))
                card_name = card.name
                card_label = Helper.get_card_label(card.id)
                member_name =  Helper.convert_member_id_to_name(card.member_id, member_dict)
                description = Helper.process_description(card.description)
                list_movements = Helper.pretty_format_list_movements(card)

                if type(description) == dict:
                    reporting_team = description['Reporting Team'] if "Reporting Team" in description else 'N/A'
                    requestor_email = description['Requestor email'] if "Requestor email" in description else 'N/A'
                    reporting_manager_email =  description['Reporting manager email'] if "Reporting manager email" in description else 'N/A'
                    type_of_requirement = description['Type of requirement'] if "Type of requirement" in description else 'N/A'

                    for movement in list_movements:
                        result.append({
                            'created_date': created_date,
                            'current_list': current_list,
                            'card_name': card_name,
                            'card_label': card_label,
                            'member_name': member_name,
                            'reporting_team': reporting_team,
                            'requestor_email': requestor_email,
                            'reporting_manager_email': reporting_manager_email, 
                            'type_of_requirement': type_of_requirement,
                            'list_from': movement['source'],
                            'list_to': movement['destination'],
                            'transaction_date': movement['datetime']
                            })
                    
                else:
                    for movement in list_movements:
                        result.append({
                            'created_date': created_date,
                            'current_list': current_list,
                            'card_name': card_name,
                            'card_label': card_label,
                            'member_name': member_name,
                            'description_pre_standardise': card.description,
                            'list_from': movement['source'],
                            'list_to': movement['destination'],
                            'transaction_date': movement['datetime']
                        })
        
        df = pd.DataFrame.from_records(result)
        df.to_csv('tickets_export.csv', index = False)


def list_all_cards_in_ad_hoc_board(client: TrelloClient) -> None:
    """
    Function to list all cards in our ad-hoc board
    """
    all_boards = client.list_boards()
    ad_hoc_board = all_boards[0]
    all_lists = ad_hoc_board.list_lists()

    for list in all_lists:
        if not list.closed:
            for card in list.list_cards():
                if not card.closed:
                    print(f'{list.name}: {card.name}')

def main() -> None:
    # Instantiate py-trello Client connection
    c1 = Client(
        api_key = 'Get Your Own Key',
        api_secret = 'Get Your Own Key',
        token = 'Get Your Own Key' 
    )
    trello_client = c1.create_client()
    
    # Instantiate Board object
    b1 = Board(trello_client)
    ad_hoc_board = b1.get_ad_hoc_board()
    
    # Instantiate Member object
    m1 = Member(ad_hoc_board)
    Helper.export_cards_to_csv(ad_hoc_board, m1)


if __name__ == "__main__":
    main()
    
