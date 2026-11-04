#include "skill_system.h"
#include "include/constants/msg.h"
#include "skill_icon_data.h"

const struct SkillInfo gSkillInfos[MAX_SKILL_NUM + 1] = {
#if (defined(SID_HpBonus) && COMMON_SKILL_VALID(SID_HpBonus))
  [SID_HpBonus] = {
    .name = MSG_SKILL_HpBonus_NAME,
    .desc = MSG_SKILL_HpBonus,
    .icon = GFX_SkillIcon_HpBonus,
  },
#endif
#if (defined(SID_StrBonus) && COMMON_SKILL_VALID(SID_StrBonus))
  [SID_StrBonus] = {
    .name = MSG_SKILL_StrBonus_NAME,
    .desc = MSG_SKILL_StrBonus,
    .icon = GFX_SkillIcon_StrBonus,
  },
#endif
  };
