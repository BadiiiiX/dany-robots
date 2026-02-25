from impl.Robot.RobotType import RobotType
from impl.Capacity.Assault.HeavyStrike import HeavyStrike
from impl.Capacity.Assault.CombatRage import CombatRage
from impl.Capacity.Defender.ReinforcedShield import ReinforcedShield
from impl.Capacity.Defender.Regeneration import Regeneration
from impl.Capacity.Agile.QuickAttack import QuickAttack
from impl.Capacity.Agile.Dodge import Dodge
from impl.Capacity.Balance.PowerfulStrike import PowerfulStrike
from impl.Capacity.Balance.QuickRecharge import QuickRecharge

ROBOT_CAPACITIES: dict[RobotType, list] = {
    RobotType.ASSAULT:  [HeavyStrike,        CombatRage],
    RobotType.DEFENDER: [ReinforcedShield,   Regeneration],
    RobotType.AGILE:    [QuickAttack,        Dodge],
    RobotType.BALANCE:  [PowerfulStrike,     QuickRecharge],
}
