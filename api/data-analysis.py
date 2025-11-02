from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

# 内联数据
LOTTERY_DATA = [
  {
    "period": "25123",
    "date": "2025-10-29",
    "front_1": 8,
    "front_2": 13,
    "front_3": 24,
    "front_4": 25,
    "front_5": 31,
    "back_1": 4,
    "back_2": 10
  },
  {
    "period": "25122",
    "date": "2025-10-27",
    "front_1": 2,
    "front_2": 3,
    "front_3": 6,
    "front_4": 16,
    "front_5": 17,
    "back_1": 4,
    "back_2": 5
  },
  {
    "period": "25121",
    "date": "2025-10-25",
    "front_1": 2,
    "front_2": 3,
    "front_3": 8,
    "front_4": 13,
    "front_5": 21,
    "back_1": 7,
    "back_2": 12
  },
  {
    "period": "25120",
    "date": "2025-10-22",
    "front_1": 11,
    "front_2": 13,
    "front_3": 22,
    "front_4": 26,
    "front_5": 35,
    "back_1": 2,
    "back_2": 8
  },
  {
    "period": "25119",
    "date": "2025-10-20",
    "front_1": 8,
    "front_2": 15,
    "front_3": 27,
    "front_4": 29,
    "front_5": 31,
    "back_1": 1,
    "back_2": 7
  },
  {
    "period": "25118",
    "date": "2025-10-18",
    "front_1": 2,
    "front_2": 8,
    "front_3": 9,
    "front_4": 12,
    "front_5": 21,
    "back_1": 4,
    "back_2": 5
  },
  {
    "period": "25117",
    "date": "2025-10-15",
    "front_1": 5,
    "front_2": 10,
    "front_3": 18,
    "front_4": 21,
    "front_5": 29,
    "back_1": 5,
    "back_2": 7
  },
  {
    "period": "25116",
    "date": "2025-10-13",
    "front_1": 2,
    "front_2": 6,
    "front_3": 16,
    "front_4": 22,
    "front_5": 29,
    "back_1": 8,
    "back_2": 12
  },
  {
    "period": "25115",
    "date": "2025-10-11",
    "front_1": 3,
    "front_2": 12,
    "front_3": 14,
    "front_4": 21,
    "front_5": 35,
    "back_1": 1,
    "back_2": 5
  },
  {
    "period": "25114",
    "date": "2025-10-08",
    "front_1": 3,
    "front_2": 8,
    "front_3": 9,
    "front_4": 12,
    "front_5": 16,
    "back_1": 1,
    "back_2": 5
  },
  {
    "period": "25113",
    "date": "2025-10-06",
    "front_1": 1,
    "front_2": 14,
    "front_3": 18,
    "front_4": 28,
    "front_5": 35,
    "back_1": 2,
    "back_2": 3
  },
  {
    "period": "25112",
    "date": "2025-09-29",
    "front_1": 3,
    "front_2": 4,
    "front_3": 21,
    "front_4": 23,
    "front_5": 24,
    "back_1": 9,
    "back_2": 12
  },
  {
    "period": "25111",
    "date": "2025-09-27",
    "front_1": 2,
    "front_2": 9,
    "front_3": 14,
    "front_4": 21,
    "front_5": 26,
    "back_1": 2,
    "back_2": 12
  },
  {
    "period": "25110",
    "date": "2025-09-24",
    "front_1": 1,
    "front_2": 15,
    "front_3": 22,
    "front_4": 30,
    "front_5": 31,
    "back_1": 2,
    "back_2": 8
  },
  {
    "period": "25109",
    "date": "2025-09-22",
    "front_1": 4,
    "front_2": 8,
    "front_3": 10,
    "front_4": 13,
    "front_5": 26,
    "back_1": 9,
    "back_2": 10
  },
  {
    "period": "25108",
    "date": "2025-09-20",
    "front_1": 14,
    "front_2": 18,
    "front_3": 21,
    "front_4": 24,
    "front_5": 29,
    "back_1": 3,
    "back_2": 6
  },
  {
    "period": "25107",
    "date": "2025-09-17",
    "front_1": 5,
    "front_2": 7,
    "front_3": 8,
    "front_4": 15,
    "front_5": 33,
    "back_1": 6,
    "back_2": 10
  },
  {
    "period": "25106",
    "date": "2025-09-15",
    "front_1": 5,
    "front_2": 6,
    "front_3": 11,
    "front_4": 26,
    "front_5": 29,
    "back_1": 5,
    "back_2": 10
  },
  {
    "period": "25105",
    "date": "2025-09-13",
    "front_1": 15,
    "front_2": 16,
    "front_3": 25,
    "front_4": 28,
    "front_5": 34,
    "back_1": 10,
    "back_2": 12
  },
  {
    "period": "25104",
    "date": "2025-09-10",
    "front_1": 2,
    "front_2": 6,
    "front_3": 9,
    "front_4": 22,
    "front_5": 34,
    "back_1": 2,
    "back_2": 8
  },
  {
    "period": "25103",
    "date": "2025-09-08",
    "front_1": 5,
    "front_2": 8,
    "front_3": 19,
    "front_4": 32,
    "front_5": 34,
    "back_1": 4,
    "back_2": 5
  },
  {
    "period": "25102",
    "date": "2025-09-06",
    "front_1": 9,
    "front_2": 10,
    "front_3": 13,
    "front_4": 26,
    "front_5": 28,
    "back_1": 2,
    "back_2": 4
  },
  {
    "period": "25101",
    "date": "2025-09-03",
    "front_1": 5,
    "front_2": 7,
    "front_3": 19,
    "front_4": 26,
    "front_5": 32,
    "back_1": 8,
    "back_2": 9
  },
  {
    "period": "25100",
    "date": "2025-09-01",
    "front_1": 26,
    "front_2": 28,
    "front_3": 32,
    "front_4": 34,
    "front_5": 35,
    "back_1": 2,
    "back_2": 7
  },
  {
    "period": "25099",
    "date": "2025-08-30",
    "front_1": 6,
    "front_2": 12,
    "front_3": 20,
    "front_4": 26,
    "front_5": 31,
    "back_1": 2,
    "back_2": 4
  },
  {
    "period": "25098",
    "date": "2025-08-27",
    "front_1": 1,
    "front_2": 7,
    "front_3": 9,
    "front_4": 10,
    "front_5": 23,
    "back_1": 10,
    "back_2": 12
  },
  {
    "period": "25097",
    "date": "2025-08-25",
    "front_1": 5,
    "front_2": 24,
    "front_3": 25,
    "front_4": 32,
    "front_5": 34,
    "back_1": 1,
    "back_2": 9
  },
  {
    "period": "25096",
    "date": "2025-08-23",
    "front_1": 2,
    "front_2": 11,
    "front_3": 17,
    "front_4": 22,
    "front_5": 24,
    "back_1": 7,
    "back_2": 9
  },
  {
    "period": "25095",
    "date": "2025-08-20",
    "front_1": 7,
    "front_2": 13,
    "front_3": 14,
    "front_4": 19,
    "front_5": 27,
    "back_1": 6,
    "back_2": 10
  },
  {
    "period": "25094",
    "date": "2025-08-18",
    "front_1": 4,
    "front_2": 9,
    "front_3": 17,
    "front_4": 30,
    "front_5": 33,
    "back_1": 5,
    "back_2": 9
  },
  {
    "period": "25093",
    "date": "2025-08-16",
    "front_1": 1,
    "front_2": 7,
    "front_3": 9,
    "front_4": 16,
    "front_5": 30,
    "back_1": 2,
    "back_2": 5
  },
  {
    "period": "25092",
    "date": "2025-08-13",
    "front_1": 4,
    "front_2": 10,
    "front_3": 17,
    "front_4": 25,
    "front_5": 32,
    "back_1": 5,
    "back_2": 7
  },
  {
    "period": "25091",
    "date": "2025-08-11",
    "front_1": 1,
    "front_2": 19,
    "front_3": 22,
    "front_4": 25,
    "front_5": 27,
    "back_1": 3,
    "back_2": 10
  },
  {
    "period": "25090",
    "date": "2025-08-09",
    "front_1": 6,
    "front_2": 14,
    "front_3": 19,
    "front_4": 22,
    "front_5": 27,
    "back_1": 1,
    "back_2": 4
  },
  {
    "period": "25089",
    "date": "2025-08-06",
    "front_1": 2,
    "front_2": 11,
    "front_3": 12,
    "front_4": 32,
    "front_5": 34,
    "back_1": 3,
    "back_2": 10
  },
  {
    "period": "25088",
    "date": "2025-08-04",
    "front_1": 8,
    "front_2": 9,
    "front_3": 10,
    "front_4": 11,
    "front_5": 35,
    "back_1": 5,
    "back_2": 11
  },
  {
    "period": "25087",
    "date": "2025-08-02",
    "front_1": 5,
    "front_2": 13,
    "front_3": 14,
    "front_4": 16,
    "front_5": 20,
    "back_1": 3,
    "back_2": 8
  },
  {
    "period": "25086",
    "date": "2025-07-30",
    "front_1": 2,
    "front_2": 6,
    "front_3": 23,
    "front_4": 24,
    "front_5": 33,
    "back_1": 1,
    "back_2": 10
  },
  {
    "period": "25085",
    "date": "2025-07-28",
    "front_1": 2,
    "front_2": 5,
    "front_3": 9,
    "front_4": 14,
    "front_5": 33,
    "back_1": 4,
    "back_2": 9
  },
  {
    "period": "25084",
    "date": "2025-07-26",
    "front_1": 9,
    "front_2": 11,
    "front_3": 13,
    "front_4": 18,
    "front_5": 29,
    "back_1": 4,
    "back_2": 11
  },
  {
    "period": "25083",
    "date": "2025-07-23",
    "front_1": 12,
    "front_2": 17,
    "front_3": 18,
    "front_4": 20,
    "front_5": 34,
    "back_1": 2,
    "back_2": 5
  },
  {
    "period": "25082",
    "date": "2025-07-21",
    "front_1": 2,
    "front_2": 3,
    "front_3": 4,
    "front_4": 12,
    "front_5": 26,
    "back_1": 1,
    "back_2": 8
  },
  {
    "period": "25081",
    "date": "2025-07-19",
    "front_1": 1,
    "front_2": 4,
    "front_3": 6,
    "front_4": 15,
    "front_5": 18,
    "back_1": 2,
    "back_2": 3
  },
  {
    "period": "25080",
    "date": "2025-07-16",
    "front_1": 9,
    "front_2": 10,
    "front_3": 18,
    "front_4": 22,
    "front_5": 24,
    "back_1": 3,
    "back_2": 12
  },
  {
    "period": "25079",
    "date": "2025-07-14",
    "front_1": 2,
    "front_2": 14,
    "front_3": 32,
    "front_4": 34,
    "front_5": 35,
    "back_1": 5,
    "back_2": 11
  },
  {
    "period": "25078",
    "date": "2025-07-12",
    "front_1": 7,
    "front_2": 10,
    "front_3": 15,
    "front_4": 21,
    "front_5": 24,
    "back_1": 5,
    "back_2": 6
  },
  {
    "period": "25077",
    "date": "2025-07-09",
    "front_1": 12,
    "front_2": 14,
    "front_3": 16,
    "front_4": 19,
    "front_5": 28,
    "back_1": 1,
    "back_2": 4
  },
  {
    "period": "25076",
    "date": "2025-07-07",
    "front_1": 11,
    "front_2": 18,
    "front_3": 22,
    "front_4": 25,
    "front_5": 29,
    "back_1": 4,
    "back_2": 12
  },
  {
    "period": "25075",
    "date": "2025-07-05",
    "front_1": 8,
    "front_2": 12,
    "front_3": 16,
    "front_4": 19,
    "front_5": 35,
    "back_1": 6,
    "back_2": 9
  },
  {
    "period": "25074",
    "date": "2025-07-02",
    "front_1": 2,
    "front_2": 11,
    "front_3": 15,
    "front_4": 18,
    "front_5": 21,
    "back_1": 5,
    "back_2": 10
  },
  {
    "period": "25073",
    "date": "2025-06-30",
    "front_1": 1,
    "front_2": 4,
    "front_3": 17,
    "front_4": 33,
    "front_5": 34,
    "back_1": 3,
    "back_2": 9
  },
  {
    "period": "25072",
    "date": "2025-06-28",
    "front_1": 4,
    "front_2": 7,
    "front_3": 15,
    "front_4": 24,
    "front_5": 29,
    "back_1": 1,
    "back_2": 4
  },
  {
    "period": "25071",
    "date": "2025-06-25",
    "front_1": 1,
    "front_2": 8,
    "front_3": 25,
    "front_4": 31,
    "front_5": 33,
    "back_1": 5,
    "back_2": 11
  },
  {
    "period": "25070",
    "date": "2025-06-23",
    "front_1": 8,
    "front_2": 9,
    "front_3": 15,
    "front_4": 20,
    "front_5": 22,
    "back_1": 4,
    "back_2": 12
  },
  {
    "period": "25069",
    "date": "2025-06-21",
    "front_1": 4,
    "front_2": 6,
    "front_3": 7,
    "front_4": 33,
    "front_5": 34,
    "back_1": 9,
    "back_2": 10
  },
  {
    "period": "25068",
    "date": "2025-06-18",
    "front_1": 1,
    "front_2": 4,
    "front_3": 17,
    "front_4": 20,
    "front_5": 22,
    "back_1": 4,
    "back_2": 10
  },
  {
    "period": "25067",
    "date": "2025-06-16",
    "front_1": 6,
    "front_2": 10,
    "front_3": 12,
    "front_4": 21,
    "front_5": 22,
    "back_1": 1,
    "back_2": 6
  },
  {
    "period": "25066",
    "date": "2025-06-14",
    "front_1": 15,
    "front_2": 18,
    "front_3": 27,
    "front_4": 28,
    "front_5": 34,
    "back_1": 3,
    "back_2": 6
  },
  {
    "period": "25065",
    "date": "2025-06-11",
    "front_1": 7,
    "front_2": 25,
    "front_3": 32,
    "front_4": 33,
    "front_5": 35,
    "back_1": 4,
    "back_2": 9
  },
  {
    "period": "25064",
    "date": "2025-06-09",
    "front_1": 5,
    "front_2": 10,
    "front_3": 18,
    "front_4": 20,
    "front_5": 34,
    "back_1": 1,
    "back_2": 8
  },
  {
    "period": "25063",
    "date": "2025-06-07",
    "front_1": 5,
    "front_2": 18,
    "front_3": 26,
    "front_4": 29,
    "front_5": 32,
    "back_1": 7,
    "back_2": 10
  },
  {
    "period": "25062",
    "date": "2025-06-04",
    "front_1": 14,
    "front_2": 20,
    "front_3": 27,
    "front_4": 28,
    "front_5": 29,
    "back_1": 6,
    "back_2": 10
  },
  {
    "period": "25061",
    "date": "2025-06-02",
    "front_1": 2,
    "front_2": 11,
    "front_3": 16,
    "front_4": 23,
    "front_5": 28,
    "back_1": 5,
    "back_2": 10
  },
  {
    "period": "25060",
    "date": "2025-05-31",
    "front_1": 12,
    "front_2": 14,
    "front_3": 19,
    "front_4": 33,
    "front_5": 34,
    "back_1": 1,
    "back_2": 7
  },
  {
    "period": "25059",
    "date": "2025-05-28",
    "front_1": 3,
    "front_2": 9,
    "front_3": 10,
    "front_4": 11,
    "front_5": 26,
    "back_1": 1,
    "back_2": 2
  },
  {
    "period": "25058",
    "date": "2025-05-26",
    "front_1": 6,
    "front_2": 11,
    "front_3": 15,
    "front_4": 21,
    "front_5": 23,
    "back_1": 1,
    "back_2": 7
  },
  {
    "period": "25057",
    "date": "2025-05-24",
    "front_1": 9,
    "front_2": 10,
    "front_3": 11,
    "front_4": 12,
    "front_5": 29,
    "back_1": 1,
    "back_2": 10
  },
  {
    "period": "25056",
    "date": "2025-05-21",
    "front_1": 12,
    "front_2": 15,
    "front_3": 28,
    "front_4": 29,
    "front_5": 32,
    "back_1": 8,
    "back_2": 11
  },
  {
    "period": "25055",
    "date": "2025-05-19",
    "front_1": 8,
    "front_2": 10,
    "front_3": 25,
    "front_4": 29,
    "front_5": 30,
    "back_1": 1,
    "back_2": 2
  },
  {
    "period": "25054",
    "date": "2025-05-17",
    "front_1": 3,
    "front_2": 12,
    "front_3": 16,
    "front_4": 21,
    "front_5": 29,
    "back_1": 1,
    "back_2": 2
  },
  {
    "period": "25053",
    "date": "2025-05-14",
    "front_1": 14,
    "front_2": 23,
    "front_3": 29,
    "front_4": 30,
    "front_5": 33,
    "back_1": 6,
    "back_2": 12
  },
  {
    "period": "25052",
    "date": "2025-05-12",
    "front_1": 2,
    "front_2": 4,
    "front_3": 11,
    "front_4": 29,
    "front_5": 30,
    "back_1": 2,
    "back_2": 8
  },
  {
    "period": "25051",
    "date": "2025-05-10",
    "front_1": 2,
    "front_2": 4,
    "front_3": 13,
    "front_4": 29,
    "front_5": 31,
    "back_1": 5,
    "back_2": 12
  },
  {
    "period": "25050",
    "date": "2025-05-07",
    "front_1": 15,
    "front_2": 18,
    "front_3": 20,
    "front_4": 21,
    "front_5": 34,
    "back_1": 4,
    "back_2": 10
  },
  {
    "period": "25049",
    "date": "2025-05-05",
    "front_1": 9,
    "front_2": 20,
    "front_3": 22,
    "front_4": 29,
    "front_5": 34,
    "back_1": 3,
    "back_2": 8
  },
  {
    "period": "25048",
    "date": "2025-05-03",
    "front_1": 2,
    "front_2": 6,
    "front_3": 17,
    "front_4": 23,
    "front_5": 35,
    "back_1": 6,
    "back_2": 11
  },
  {
    "period": "25047",
    "date": "2025-04-30",
    "front_1": 3,
    "front_2": 10,
    "front_3": 11,
    "front_4": 12,
    "front_5": 21,
    "back_1": 2,
    "back_2": 3
  },
  {
    "period": "25046",
    "date": "2025-04-28",
    "front_1": 4,
    "front_2": 10,
    "front_3": 15,
    "front_4": 20,
    "front_5": 34,
    "back_1": 4,
    "back_2": 7
  },
  {
    "period": "25045",
    "date": "2025-04-26",
    "front_1": 8,
    "front_2": 11,
    "front_3": 21,
    "front_4": 23,
    "front_5": 27,
    "back_1": 3,
    "back_2": 8
  },
  {
    "period": "25044",
    "date": "2025-04-23",
    "front_1": 15,
    "front_2": 17,
    "front_3": 21,
    "front_4": 22,
    "front_5": 26,
    "back_1": 2,
    "back_2": 8
  },
  {
    "period": "25043",
    "date": "2025-04-21",
    "front_1": 3,
    "front_2": 16,
    "front_3": 20,
    "front_4": 21,
    "front_5": 27,
    "back_1": 9,
    "back_2": 11
  },
  {
    "period": "25042",
    "date": "2025-04-19",
    "front_1": 6,
    "front_2": 8,
    "front_3": 11,
    "front_4": 18,
    "front_5": 20,
    "back_1": 5,
    "back_2": 11
  },
  {
    "period": "25041",
    "date": "2025-04-16",
    "front_1": 3,
    "front_2": 4,
    "front_3": 21,
    "front_4": 22,
    "front_5": 27,
    "back_1": 5,
    "back_2": 11
  },
  {
    "period": "25040",
    "date": "2025-04-14",
    "front_1": 2,
    "front_2": 8,
    "front_3": 16,
    "front_4": 31,
    "front_5": 32,
    "back_1": 4,
    "back_2": 12
  },
  {
    "period": "25039",
    "date": "2025-04-12",
    "front_1": 3,
    "front_2": 7,
    "front_3": 14,
    "front_4": 15,
    "front_5": 19,
    "back_1": 6,
    "back_2": 10
  },
  {
    "period": "25038",
    "date": "2025-04-09",
    "front_1": 7,
    "front_2": 8,
    "front_3": 20,
    "front_4": 26,
    "front_5": 34,
    "back_1": 8,
    "back_2": 9
  },
  {
    "period": "25037",
    "date": "2025-04-07",
    "front_1": 5,
    "front_2": 20,
    "front_3": 23,
    "front_4": 27,
    "front_5": 31,
    "back_1": 4,
    "back_2": 6
  },
  {
    "period": "25036",
    "date": "2025-04-05",
    "front_1": 4,
    "front_2": 7,
    "front_3": 13,
    "front_4": 27,
    "front_5": 30,
    "back_1": 2,
    "back_2": 6
  },
  {
    "period": "25035",
    "date": "2025-04-02",
    "front_1": 22,
    "front_2": 25,
    "front_3": 28,
    "front_4": 29,
    "front_5": 30,
    "back_1": 4,
    "back_2": 8
  },
  {
    "period": "25034",
    "date": "2025-03-31",
    "front_1": 4,
    "front_2": 15,
    "front_3": 22,
    "front_4": 28,
    "front_5": 33,
    "back_1": 6,
    "back_2": 8
  },
  {
    "period": "25033",
    "date": "2025-03-29",
    "front_1": 1,
    "front_2": 2,
    "front_3": 8,
    "front_4": 10,
    "front_5": 33,
    "back_1": 10,
    "back_2": 12
  },
  {
    "period": "25032",
    "date": "2025-03-26",
    "front_1": 12,
    "front_2": 22,
    "front_3": 25,
    "front_4": 27,
    "front_5": 28,
    "back_1": 1,
    "back_2": 2
  },
  {
    "period": "25031",
    "date": "2025-03-24",
    "front_1": 14,
    "front_2": 18,
    "front_3": 20,
    "front_4": 25,
    "front_5": 35,
    "back_1": 1,
    "back_2": 7
  },
  {
    "period": "25030",
    "date": "2025-03-22",
    "front_1": 3,
    "front_2": 9,
    "front_3": 14,
    "front_4": 24,
    "front_5": 28,
    "back_1": 6,
    "back_2": 7
  },
  {
    "period": "25029",
    "date": "2025-03-19",
    "front_1": 5,
    "front_2": 9,
    "front_3": 26,
    "front_4": 31,
    "front_5": 33,
    "back_1": 3,
    "back_2": 10
  },
  {
    "period": "25028",
    "date": "2025-03-17",
    "front_1": 6,
    "front_2": 8,
    "front_3": 20,
    "front_4": 25,
    "front_5": 29,
    "back_1": 3,
    "back_2": 7
  },
  {
    "period": "25027",
    "date": "2025-03-15",
    "front_1": 3,
    "front_2": 6,
    "front_3": 11,
    "front_4": 13,
    "front_5": 20,
    "back_1": 1,
    "back_2": 11
  },
  {
    "period": "25026",
    "date": "2025-03-12",
    "front_1": 2,
    "front_2": 3,
    "front_3": 7,
    "front_4": 17,
    "front_5": 30,
    "back_1": 1,
    "back_2": 9
  },
  {
    "period": "25025",
    "date": "2025-03-10",
    "front_1": 3,
    "front_2": 6,
    "front_3": 8,
    "front_4": 10,
    "front_5": 25,
    "back_1": 3,
    "back_2": 7
  },
  {
    "period": "25024",
    "date": "2025-03-08",
    "front_1": 6,
    "front_2": 12,
    "front_3": 13,
    "front_4": 16,
    "front_5": 23,
    "back_1": 5,
    "back_2": 8
  }
]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if not LOTTERY_DATA:
                raise Exception("数据为空")
            
            total_draws = len(LOTTERY_DATA)
            
            # 前区统计
            front_freq = {}
            for record in LOTTERY_DATA:
                for i in range(1, 6):
                    num = record[f'front_{i}']
                    front_freq[num] = front_freq.get(num, 0) + 1
            
            # 后区统计
            back_freq = {}
            for record in LOTTERY_DATA:
                for i in range(1, 3):
                    num = record[f'back_{i}']
                    back_freq[num] = back_freq.get(num, 0) + 1
            
            hot_front = sorted(front_freq.items(), key=lambda x: x[1], reverse=True)
            hot_back = sorted(back_freq.items(), key=lambda x: x[1], reverse=True)
            
            response = {
                'status': 'success',
                'analysis': {
                    'data_overview': {
                        'total_draws': total_draws,
                        'analysis_period': f'{LOTTERY_DATA[-1]["period"]} 至 {LOTTERY_DATA[0]["period"]}',
                        'last_update': LOTTERY_DATA[0]['date']
                    },
                    'front_zone_analysis': {
                        'most_frequent': [x[0] for x in hot_front[:5]],
                        'hot_numbers': [x[0] for x in hot_front[:10]]
                    },
                    'back_zone_analysis': {
                        'most_frequent': [x[0] for x in hot_back[:2]],
                        'hot_numbers': [x[0] for x in hot_back[:5]]
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
