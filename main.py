import requests
import bs4
import argparse
from dataclasses import dataclass
from typing import List, Dict,Union,Tuple

@dataclass
class Build:
    strong_against: List[str]
    weak_against: List[str]
    skill_dict: Dict[str, str]
    tips: str

@dataclass
class Guide:
    when_strong: Dict[str, str]
    tips_for_stage_of_game: Dict[str, str]
    strengths: str = ""
    weaknesses: str = ""

@dataclass
class Meta_Data:
    top: List[str]
    mid: List[str]
    jungle: List[str]
    bot: List[str]
    support: List[str]

class Scraper():
    def __init__(self, champion_or_meta):
        self.champion_or_meta = champion_or_meta
        self.meta_link = "https://mobalytics.gg/blog/lol-tier-list-for-climbing-solo-queue/"
        self.champion_link = f"https://app.mobalytics.gg/lol/champions/{self.champion_or_meta}/"
    
    def get_soup(self) -> Union[bs4.BeautifulSoup, Tuple[bs4.BeautifulSoup]]:
        session = requests.Session()
        
        if self.champion_or_meta == "meta":
            r = session.get(self.meta_link)
            soup = bs4.BeautifulSoup(r.content,"lxml")
            return soup 
        else:
            r_build = session.get(self.champion_link+"build")
            build_soup = bs4.BeautifulSoup(r_build.content,"lxml")

            r_guide = session.get(self.champion_link+"guide")
            guide_soup = bs4.BeautifulSoup(r_guide.content,"lxml")
            
            return build_soup,guide_soup

    def parse_build(self, soup:bs4) -> Build: 
        skill_dict = {}
        strong_against = []
        weak_against = []
        
       
        against_all = soup.find_all("div",{"class":"m-1nhoed7 ez6mgdl1"})
        
        for champion_box in against_all[0].find_all("a"):

            champion = champion_box.get("href").split("/lol/champions/")[1].replace("/build","")
            
            weak_against.append(champion)

        for champion_box in against_all[1].find_all("a"):
            champion = champion_box.get("href").split("/lol/champions/")[1].replace("/build","")
            strong_against.append(champion)

        skill_diagram = soup.find("div",{"class":"m-1uv578k"}).find_all("div",{"m-af8mp8"})
        
        for level,ability in enumerate(skill_diagram):
            skill_dict[level+1] = ability.text.strip()

        tips = soup.find("div", {"class":"m-17ylhtw e1n6zbyc1"}).text.strip()

        build_data = Build(weak_against=weak_against,strong_against=strong_against,skill_dict=skill_dict,tips=tips)

        return build_data
            
    def parse_guide(self, soup:bs4) -> Guide:
        strengths, weaknesses, when_strong_list = "", "", []
        tips_for_stage_of_game = {}

        strength_weakness = soup.find_all("div", {"class": "m-1s0gpse"})
        strengths = strength_weakness[0].text.strip()
        weaknesses = strength_weakness[1].text.strip()
        
        gameplay = soup.find("div", {"class": "m-11kzyeb e1n6zbyc1"}).find_all("span")
        for strength in gameplay:
            strength = strength.text.strip()
            if strength in ["Weak", "Average", "Strong"]:
                when_strong_list.append(strength)

        when_strong = {
            "early game": when_strong_list[0],
            "mid game": when_strong_list[1],
            "late game": when_strong_list[2]
        }

        tips_for_stages = soup.find_all("div", {"class":"m-10295yi"})
       
        for info_stage in tips_for_stages:
            for stage in ["early game", "mid game", "late game"]:
                tips_for_stage_of_game[stage] = info_stage.text.strip()

        guide_data = Guide(
            tips_for_stage_of_game=tips_for_stage_of_game,
            strengths=strengths,
            weaknesses=weaknesses,
            when_strong=when_strong
        )
        return guide_data

    def parse_meta(self, soup:bs4) -> Meta_Data:

        champ_lists = {
        'top': [],
        'jungle': [],
        'mid': [],
        'bot': [],
        'support': []
        }

        sections = soup.find_all("div", {"class": "section"})

        for idx, role in enumerate(['top', 'jungle', 'mid', 'bot', 'support']):
            champs = sections[idx+1].find("div", {"class": "champions"}).find_all("div", {"class": "champion"})
            champ_lists[role] = [champ.text.strip() for champ in champs]

        meta_data = Meta_Data(**champ_lists)
       
        return meta_data
    
    def run(self):
        if self.champion_or_meta == "meta":
            soup = self.get_soup()
            meta_data = self.parse_meta(soup=soup)
            return meta_data
        else:
            build_soup,guide_soup = self.get_soup()
            build_data = self.parse_build(soup=build_soup)
            guide_data = self.parse_guide(soup=guide_soup)
            return build_data,guide_data



class Champion():
    def __init__(self, name):
        self.name = name
        self.skill_order = {}
        self.strong_against = []
        self.weak_against = []
        self.tips = ""
        self.when_strong = {}
        self.tips_for_stage_of_game = {}
        self.strengths = ""
        self.weaknesses = ""

    def __str__(self):
        return f'{self.name} here is the info for {self.name}, \n --------------------------------- \n \
        this is the skill order{self.skill_order}, \n ----------------------------------------- \n \
        he is strong against {self.strong_against} , \n ----------------------------------------- \n \
        and weak against {self.weak_against} , \n ----------------------------------------- \n \
        Some tips to follow are {self.tips} , \n ----------------------------------------- \n \
        {self.name} is typically strong {self.when_strong} , \n ----------------------------------------- \n \
         some tips for early games are {self.tips_for_stage_of_game["early game"]} , \n ----------------------------------------- \n \
        some tips for mid games are {self.tips_for_stage_of_game["mid game"]} , \n ----------------------------------------- \n \
         some tips for late games are {self.tips_for_stage_of_game["late game"]} , \n ----------------------------------------- \n \
        some strengths {self.strengths}, \n ----------------------------------------- \n \
            some weakness {self.weaknesses}'
        
    def get_champion_info(self):
        scraper = Scraper(champion_or_meta = self.name)
        build_data,guide_data = scraper.run()
        self.skill_order = build_data.skill_dict
        self.weak_against = build_data.weak_against
        self.strong_against = build_data.strong_against
        self.tips = build_data.tips
        self.when_strong = guide_data.when_strong
        self.tips_for_stage_of_game = guide_data.tips_for_stage_of_game
        self.strengths = guide_data.strengths
        self.weaknesses = guide_data.weaknesses


class Meta():
    def _init__(self):
        self.top = []
        self.mid = []
        self.jungle = []
        self.bot = []
        self.support = []

    def __str__(self):
        return f"This is the meta for each lane:\n\
                top: {self.top}\n\
                mid: {self.mid}\n\
                jungle: {self.jungle}\n\
                bot: {self.bot}\n\
                support: {self.support}"

    def get_meta_info(self):
        scraper = Scraper(champion_or_meta = "meta")
        meta_data = scraper.run()
        self.top = meta_data.top
        self.mid = meta_data.mid
        self.jungle = meta_data.jungle
        self.bot = meta_data.bot
        self.support = meta_data.support

def main():
    parser = argparse.ArgumentParser(description='This tool is for creating a terminal based way of getting league of legends meta and champion information')
    parser.add_argument('--type', default='meta', choices=['meta', 'champion'], help='Type of input')
    parser.add_argument('--name', required=False if parser.get_default('type') == 'meta' else True, help='Name of the input')
    args = parser.parse_args()

    if args.type == 'meta':
        meta = Meta()
        meta.get_meta_info()
        print(meta)
        
    elif args.type == 'champion':  
        champion_name = args.name.lower()
        champion = Champion(name=champion_name)
        champion.get_champion_info()
        print(champion)
        


if __name__ == "__main__":
    main()