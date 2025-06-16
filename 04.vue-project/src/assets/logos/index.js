// 直接导入所有图片 - 这样Vite会处理这些图片并将其包含在构建中
import ABNB_IMG from '../../assets/logos/ABNB_logo.png';
import ALMOSAFER_IMG from '../../assets/logos/Almosafer_logo.png';
import BKNG_IMG from '../../assets/logos/BKNG_logo.png';
import CLEARTRIP_IMG from '../../assets/logos/Cleartrip_logo.png';
import DESP_IMG from '../../assets/logos/DESP_logo.png';
import EASEMYTRIP_IMG from '../../assets/logos/EASEMYTRIP_logo.png';
import EDR_IMG from '../../assets/logos/EDR_logo.png';
import ETRAVELI_IMG from '../../assets/logos/Etraveli_logo.png';
import EXPE_IMG from '../../assets/logos/EXPE_logo.png';
import FLT_IMG from '../../assets/logos/FlightCentre_logo.png';
import IXIGO_IMG from '../../assets/logos/IXIGO_logo.png';
import KIWI_IMG from '../../assets/logos/Kiwi_logo.png';
import LMN_IMG from '../../assets/logos/LMN_logo.png';
import MMYT_IMG from '../../assets/logos/MMYT_logo.png';
import OWW_IMG from '../../assets/logos/Orbitz_logo.png';
import PCLN_IMG from '../../assets/logos/PCLN_logo.png';
import SEERA_IMG from '../../assets/logos/SEERA_logo.png';
import SKYSCANNER_IMG from '../../assets/logos/Skyscanner_logo.png';
import TCOM_IMG from '../../assets/logos/TCOM_logo.png';
import TRAVELOCITY_IMG from '../../assets/logos/Travelocity_logo.png';
import TRAVELOKA_IMG from '../../assets/logos/Traveloka_logo.png';
import TRIP_IMG from '../../assets/logos/TRIP_logo.png';
import TRVG_IMG from '../../assets/logos/TRVG_logo.png';
import WEB_IMG from '../../assets/logos/Webjet_logo.png';
import WEGO_IMG from '../../assets/logos/Wego_logo.png';
import YTRA_IMG from '../../assets/logos/Yatra_logo.png';

// 将导入的图片映射到公司代码
const logoImageMap = {
  'ABNB': ABNB_IMG,
  'Almosafer': ALMOSAFER_IMG,
  'BKNG': BKNG_IMG,
  'Cleartrip': CLEARTRIP_IMG,
  'DESP': DESP_IMG,
  'EaseMyTrip': EASEMYTRIP_IMG,
  'EDR': EDR_IMG,
  'Etraveli': ETRAVELI_IMG,
  'EXPE': EXPE_IMG,
  'FLT': FLT_IMG,
  'IXIGO': IXIGO_IMG,
  'Kiwi': KIWI_IMG,
  'LMN': LMN_IMG,
  'MMYT': MMYT_IMG,
  'OWW': OWW_IMG,
  'PCLN': PCLN_IMG,
  'SEERA': SEERA_IMG,
  'Skyscanner': SKYSCANNER_IMG,
  'TCOM': TCOM_IMG,
  'Travelocity': TRAVELOCITY_IMG,
  'Traveloka': TRAVELOKA_IMG,
  'TRIP': TRIP_IMG,
  'TRVG': TRVG_IMG,
  'WEB': WEB_IMG,
  'Wego': WEGO_IMG,
  'YTRA': YTRA_IMG,
};

// 导出个别logo
export const ABNB_LOGO = logoImageMap['ABNB'];
export const ALMOSAFER_LOGO = logoImageMap['Almosafer'];
export const BKNG_LOGO = logoImageMap['BKNG'];
export const CLEARTRIP_LOGO = logoImageMap['Cleartrip'];
export const DESP_LOGO = logoImageMap['DESP'];
export const EASEMYTRIP_LOGO = logoImageMap['EaseMyTrip'];
export const EDR_LOGO = logoImageMap['EDR'];
export const ETRAVELI_LOGO = logoImageMap['Etraveli'];
export const EXPE_LOGO = logoImageMap['EXPE'];
export const FLT_LOGO = logoImageMap['FLT'];
export const IXIGO_LOGO = logoImageMap['IXIGO'];
export const KIWI_LOGO = logoImageMap['Kiwi'];
export const LMN_LOGO = logoImageMap['LMN'];
export const MMYT_LOGO = logoImageMap['MMYT'];
export const OWW_LOGO = logoImageMap['OWW'];
export const PCLN_LOGO = logoImageMap['PCLN'];
export const SEERA_LOGO = logoImageMap['SEERA'];
export const SKYSCANNER_LOGO = logoImageMap['Skyscanner'];
export const TCOM_LOGO = logoImageMap['TCOM'];
export const TRAVELOCITY_LOGO = logoImageMap['Travelocity'];
export const TRAVELOKA_LOGO = logoImageMap['Traveloka'];
export const TRIP_LOGO = logoImageMap['TRIP'];
export const TRVG_LOGO = logoImageMap['TRVG'];
export const WEB_LOGO = logoImageMap['WEB'];
export const WEGO_LOGO = logoImageMap['Wego'];
export const YTRA_LOGO = logoImageMap['YTRA'];

// 导出映射对象
export const logoMap = logoImageMap; 