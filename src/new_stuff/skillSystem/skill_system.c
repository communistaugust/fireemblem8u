#include "skill_system.h"

u16 GetSkillName(int sid){
  return gSkillInfos[sid].name;
}

u16 GetSkillDesc(int sid){
  return gSkillInfos[sid].desc;
}