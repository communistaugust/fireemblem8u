#include "icon.h"
#include "global.h"
#include "skill_system.h"

const u8 *IconGetterVanilla(const u8 index)
{
	return item_icon_tiles[index];
}

const u8 *GetAffinIcon(const u8 index)
{
	return gAffinIcons[index];
}

const u8 *GetMountIcon(const u8 index)
{
	return gMountIcons[index];
}

const u8 *GetWTypeIcon(const u8 index)
{
	return gWTypeIcons[index];
}

const u8 *GetSkillIcon(const u8 index)
{
	return gSkillInfos[index].icon;
}