from socket import *
from struct import *
from statistics import mean
from math import floor
from itertools import zip_longest
from enum import IntFlag
from os import system


def clear():
    system('cls')


class LapValidFlags(IntFlag):
    Lap, Sector1, Sector2, Sector3 = 0x1, 0x2, 0x4, 0x8


udpIP = "127.0.0.1"
udpPort = 20777
udpServer = socket(AF_INET, SOCK_DGRAM)
udpServer.bind((udpIP, udpPort))

PacketHeader = '<H4BQfI2B'

PacketFinalClass = '6BId3B8s8s'

marshalZone = 'fb'
weatherSample = '3B4bB'
PacketSessionData = '<B2bBHBbB2H6B' + str(21 * calcsize(marshalZone)) \
                    + 's3B' + str(56 * calcsize(weatherSample)) + "s2B3I12B"

lapHistory = 'L3HB'
tyreHistory = '3B'
PacketSessionHistory = '<7B' + str(100 * calcsize(lapHistory)) + 's' + str(8 * calcsize(tyreHistory)) + 's'

EventPacket = '<4s8s'

PB_List, PB_Sector, AI_Times, SessionData = [0], 3*[0], {}, {}

print('Waiting for results ...')

while True:
    udpData = udpServer.recvfrom(2048)
    clientData = udpData[0]
    _, _, _, _, PacketID, SessionID, _, _, PlayerIndex, _ = unpack(PacketHeader, clientData[:calcsize(PacketHeader)])
    match PacketID:
        case 1:
            PacketData = unpack(PacketSessionData, clientData[calcsize(PacketHeader):])
            SessionData.update({'Difficulty': PacketData[22], 'Type': PacketData[5]})
        case 3:
            PacketData = unpack(EventPacket, clientData[calcsize(PacketHeader):])
            EventCode, EventData = PacketData
            match EventCode.decode('utf-8'):
                case 'SSTA' | 'SEND':
                    SessionData.update({'Event': EventCode.decode('utf-8')})

        case 8:
            if SessionData.get('Type') != 9 or SessionData.get('ID') == SessionID:
                continue
            SessionData.update({'ID': SessionID})

            FinalClass = unpack('<' + PacketFinalClass * 22, clientData[calcsize(PacketHeader + 'B'):])
            PlayerOffset = PlayerIndex*13
            PlayerPos = FinalClass[PlayerOffset]
            PlayerTime = FinalClass[PlayerOffset + 6]

            if PlayerTime != 0:
                PB_List.append(PlayerTime)
                if 0 in PB_List:
                    PB_List.remove(0)
                PB_List.sort()

            for ID in [x for x in range(0, len(FinalClass), 13) if x != PlayerOffset]:
                AIPos = FinalClass[ID]
                if AIPos == 1 or (AIPos == 2 and PlayerPos == 1):
                    AITime = [FinalClass[ID + 6]]

                    if SessionData.get('Difficulty') in AI_Times:
                        AIBracket = AI_Times.get(SessionData.get('Difficulty'))
                        if not AIBracket.get('Generated'):
                            AITime.extend(AIBracket.get('Time'))

                    AI_Times.update({SessionData.get('Difficulty'): {'Time': AITime, 'Generated': False}})

            clear()
            PB_Time, PB3_Time, PB10_Time, AVG, SOB = \
                min(PB_List),\
                mean(PB_List[:3]),\
                mean(PB_List[:10]),\
                mean(PB_List),\
                0 if 0 in PB_Sector else sum(PB_Sector)
            print(*[f'{floor(Value / (1000 * 60)):>1d}:{(Value / 1000) % 60:>06.3f}' for Value in PB_List[:10]])
            print(*[f'{(Value / 1000) % 60:>06.3f}' for Value in PB_Sector])
            print(f'Personal :'
                  f'{floor(SOB / (1000 * 60)):>6d}:{(SOB / 1000) % 60:>06.3f}'
                  f'|{floor(PB_Time / (1000 * 60)):>1d}:{(PB_Time / 1000) % 60:>06.3f}'
                  f'|{floor(PB3_Time / (1000 * 60)):>1d}:{(PB3_Time / 1000) % 60:>06.3f}'
                  f'|{floor(PB10_Time / (1000 * 60)):>1d}:{(PB10_Time / 1000) % 60:>06.3f}'
                  f'|{floor(AVG / (1000 * 60)):>1d}:{(AVG / 1000) % 60:>06.3f}')
            print('-' * 60)
            print(f'{"AI":^4s}{"Time":^10s}{"SoB":>7s}{"PB":>9s}{"AVG-T3":>11s}{"AVG-T10":>9s}{"AVG":>7s}')

            Filtered = [(Key, Value['Time']) for Key, Value in AI_Times.items() if not Value['Generated']]
            for Current, Next in zip_longest(sorted(Filtered), sorted(Filtered)[1:]):
                CurrentAI, CurrentTime = Current
                NextAI, NextTime = Next if Next is not None else (CurrentAI + 1, CurrentTime)
                CurrentAVG, NextAVG = mean(CurrentTime), mean(NextTime)
                Gap = NextAI - CurrentAI
                for Step in range(Gap):
                    Generated = Step != 0
                    Time = CurrentAVG - (((CurrentAVG - NextAVG) / Gap) * Step)
                    Difficulty = CurrentAI + Step
                    AI_Times.update(
                        {Difficulty: {'Time': [Time] if Generated else CurrentTime, 'Generated': Generated}})
                    print(f'{"*" + str(Difficulty) if Generated else Difficulty:^4}'
                          f'{floor(Time / (1000 * 60)):>2d}:{(Time / 1000) % 60:06.3f}'
                          f'{(SOB - Time) / 1000:>+10.3f}'
                          f'{(PB_Time - Time) / 1000:>+9.3f}'
                          f'{(PB3_Time - Time) / 1000:>+9.3f}'
                          f'{(PB10_Time - Time) / 1000:>+9.3f}'
                          f'{(AVG - Time) / 1000:>+9.3f}')

            print('Suggested:{recSOB:>11}{recPB:>9}{recPB3:>9}{recPB10:>9}{recAVG:>9}'.format(
                recPB=min([Key for Key, Value in AI_Times.items() if PB_Time - mean(Value['Time']) > 0],
                          default=max(AI_Times)),
                recPB3=min([Key for Key, Value in AI_Times.items() if PB3_Time - mean(Value['Time']) > 0],
                           default=max(AI_Times)),
                recPB10=min([Key for Key, Value in AI_Times.items() if PB10_Time - mean(Value['Time']) > 0],
                            default=max(AI_Times)),
                recAVG=min([Key for Key, Value in AI_Times.items() if AVG - mean(Value['Time']) > 0],
                           default=max(AI_Times)),
                recSOB=min([Key for Key, Value in AI_Times.items() if SOB - mean(Value['Time']) > 0],
                           default=max(AI_Times))))
            print('Waiting for results ...')

        case 11:
            if SessionData.get('Type') != 9 or SessionData.get('Event') != 'SEND':
                continue
            SessionHistory = unpack(PacketSessionHistory, clientData[calcsize(PacketHeader):])
            if SessionHistory[0] == PlayerIndex:
                LapHistory = unpack('<' + 100 * (str(calcsize(lapHistory)) + 's'), SessionHistory[7])
                Lap1 = unpack('<' + lapHistory, LapHistory[0])
                Validity = LapValidFlags(Lap1[4])
                PB_Sector = [min([Time for TimeIndex, Time in enumerate(SectorTimes)
                                  if (2 ** SectorIndex & Validity or TimeIndex == 0) and Time > 0], default=0)
                             for SectorIndex, SectorTimes in enumerate(zip(PB_Sector, Lap1[1:]), start=1)]
