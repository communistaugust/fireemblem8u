#ifndef SKILL_SYSTEM_H
#define SKILL_SYSTEM_H
#include "global.h"

#ifndef MAX_SKILL_NUM
#define MAX_SKILL_NUM 0x3FF
#endif

struct SkillInfo {
    const u8 *icon;
    u16 name, desc;
	u8 additional_infos;
};

extern const struct SkillInfo gSkillInfos[MAX_SKILL_NUM + 1];
#define SID_HpBonus 0x001
#define SID_StrBonus 0x002
#define SID_MagBonus 0x003
#define SID_SklBonus 0x004
#define SID_SpdBonus 0x005
#define SID_LckBonus 0x006
#define SID_DefBonus 0x007
#define SID_ResBonus 0x008
#define SID_MovBonus 0x009
#define SID_Resolve 0x00A
#define SID_DefiantStr 0x00B


#define SKILL_INDEX_REAL(sid) ((sid) & 0xFF)


#define COMMON_SKILL_VALID(sid) (sid > 0x000 && sid < 0x400)

u16 GetSkillName(int sid);
u16 GetSkillDesc(int sid);
#endif //SKILL_SYSTEM_H
