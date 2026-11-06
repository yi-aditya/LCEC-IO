# M2 - Fixes applied to the imported symbols

easyeda2kicad output is generic. `scripts/fix_symbols.py` corrects it from the datasheets (re-runnable). Pin electrical types are also set on every symbol (power in/out, input, output, bidirectional, open collector, no connect, passive); before this every pin was 'unspecified', which would make ERC silent.

The log below is produced by running the fixer on the raw EasyEDA import (`python3 -I scripts/fix_symbols.py --lib <raw copy> --log docs/review/M2-symbol-fixes.md`). Three parts have no EasyEDA data (404) and were made by `scripts/make_manual_parts.py`: C5272782 Keystone 7770 (footprint drawn from the Keystone drawing) and the cable plugs C440881 and C440884.

| Symbol | Change |
|---|---|
| ECS-3225MVQ-250-CN-TR | field 'LCSC Part' renamed to 'LCSC' |
| ECS-3225MVQ-250-CN-TR | Datasheet: 'https://www.lcsc.com/datasheet/C2595919.' -> 'https://datasheet.lcsc.com/datasheet/pdf/c3df565c0c0763e3f49' |
| ECS-3225MVQ-250-CN-TR | Reference 'U' -> 'X' |
| ECS-3225MVQ-250-CN-TR | pin 1: 'Tri-state' -> 'OE' (datasheet) |
| PZ127-2-05-S | field 'LCSC Part' renamed to 'LCSC' |
| PZ127-2-05-S | Manufacturer: 'HCTL(华灿天禄)' -> 'HCTL' |
| PZ127-2-05-S | Datasheet: 'https://www.lcsc.com/datasheet/C3975188.' -> 'https://datasheet.lcsc.com/datasheet/pdf/1e6da833c9822e59490' |
| PZ127-2-05-S | Reference 'U' -> 'J' |
| PZ254V-11-03P_C2937625 | field 'LCSC Part' renamed to 'LCSC' |
| PZ254V-11-03P_C2937625 | Manufacturer: 'XFCN(兴飞)' -> 'XFCN' |
| PZ254V-11-03P_C2937625 | Datasheet: 'https://www.lcsc.com/datasheet/C2937625.' -> 'https://datasheet.lcsc.com/datasheet/pdf/3b85a1cdf6ed945f2e2' |
| PZ254V-11-03P_C2937625 | Reference 'H' -> 'J' |
| LAN9252I_PT | field 'LCSC Part' renamed to 'LCSC' |
| LAN9252I_PT | Manufacturer: 'MICROCHIP(美国微芯)' -> 'MICROCHIP' |
| LAN9252I_PT | Datasheet: 'https://lcsc.com/product-detail/Interfac' -> 'https://datasheet.lcsc.com/datasheet/pdf/9454995c72fa47189fb' |
| LAN9252I_PT | pin 5: 'VDD3' -> 'VDD33' (datasheet) |
| 24LC32AT-I_SN | field 'LCSC Part' renamed to 'LCSC' |
| 24LC32AT-I_SN | Manufacturer: 'MICROCHIP(美国微芯)' -> 'MICROCHIP' |
| 24LC32AT-I_SN | Datasheet: 'https://www.lcsc.com/datasheet/C615715.p' -> 'https://datasheet.lcsc.com/datasheet/pdf/984d85295941735f833' |
| HY911105AE | field 'LCSC Part' renamed to 'LCSC' |
| HY911105AE | Manufacturer: 'HANRUN(汉仁)' -> 'HANRUN(Zhongshan HanRun Elec)' |
| HY911105AE | Datasheet: 'https://lcsc.com/product-detail/RJ45_HY9' -> 'https://datasheet.lcsc.com/datasheet/pdf/3ce9e7a3e230471ebb3' |
| HY911105AE | pin 5: '5' -> 'RD_CT' (datasheet) |
| HY911105AE | pin 4: '4' -> 'TD_CT' (datasheet) |
| HY911105AE | pin 9: '9' -> 'LEDG_A' (datasheet) |
| HY911105AE | pin 10: '10' -> 'LEDG_K' (datasheet) |
| HY911105AE | pin 12: '12' -> 'LEDY_A' (datasheet) |
| HY911105AE | pin 11: '11' -> 'LEDY_K' (datasheet) |
| URB2403S-6WR3_C5369843 | field 'LCSC Part' renamed to 'LCSC' |
| URB2403S-6WR3_C5369843 | Manufacturer: 'YLPTEC(易川)' -> 'YLPTEC' |
| URB2403S-6WR3_C5369843 | Datasheet: 'https://www.lcsc.com/datasheet/C5369843.' -> 'https://datasheet.lcsc.com/datasheet/pdf/7f11f97d067d14880ec' |
| URB2405S-6WR3_C3031185 | field 'LCSC Part' renamed to 'LCSC' |
| URB2405S-6WR3_C3031185 | Manufacturer: 'YLPTEC(易川)' -> 'YLPTEC' |
| URB2405S-6WR3_C3031185 | Datasheet: 'https://www.lcsc.com/datasheet/C3031185.' -> 'https://datasheet.lcsc.com/datasheet/pdf/7f11f97d067d14880ec' |
| URB2415S-6WR3_C5369844 | field 'LCSC Part' renamed to 'LCSC' |
| URB2415S-6WR3_C5369844 | Manufacturer: 'YLPTEC(易川)' -> 'YLPTEC' |
| URB2415S-6WR3_C5369844 | Datasheet: 'https://www.lcsc.com/datasheet/C5369844.' -> 'https://datasheet.lcsc.com/datasheet/pdf/7f11f97d067d14880ec' |
| SMBJ33A_C320242 | field 'LCSC Part' renamed to 'LCSC' |
| SMBJ33A_C320242 | Manufacturer: 'LGE(鲁光)' -> 'LGE' |
| SMBJ33A_C320242 | Datasheet: 'https://lcsc.com/product-detail/Others_L' -> 'https://datasheet.lcsc.com/datasheet/pdf/7291596a24f0c91c915' |
| SMBJ33A_C320242 | pin 2: '2' -> 'A' (datasheet) |
| SMBJ33A_C320242 | pin 1: '1' -> 'K' (datasheet) |
| SS54_C22452 | field 'LCSC Part' renamed to 'LCSC' |
| SS54_C22452 | Manufacturer: 'MDD(辰达半导体)' -> 'MDD(Microdiode Semiconductor)' |
| SS54_C22452 | Datasheet: 'https://lcsc.com/product-detail/Schottky' -> 'https://datasheet.lcsc.com/datasheet/pdf/3d29bdcdc3c46ec127d' |
| 1A250VAC | field 'LCSC Part' renamed to 'LCSC' |
| 1A250VAC | Manufacturer: 'xcfuse(旭程)' -> 'Xucheng Elec' |
| 1A250VAC | Datasheet: 'https://lcsc.com/product-detail/Glass-Fu' -> 'https://datasheet.lcsc.com/datasheet/pdf/0720ae667fc4987d8d7' |
| 1A250VAC | accessory, not on the PCB: 2 placeholder pin(s) and footprint removed, set 'exclude from board' |
| 3A250VACGlasstubefuse | field 'LCSC Part' renamed to 'LCSC' |
| 3A250VACGlasstubefuse | Manufacturer: 'xcfuse(旭程)' -> 'Xucheng Elec' |
| 3A250VACGlasstubefuse | Datasheet: 'https://lcsc.com/product-detail/Glass-Fu' -> 'https://datasheet.lcsc.com/datasheet/pdf/c896b0d036f7d311cda' |
| 3A250VACGlasstubefuse | accessory, not on the PCB: 2 placeholder pin(s) and footprint removed, set 'exclude from board' |
| RVT1H470M060747UF50V | field 'LCSC Part' renamed to 'LCSC' |
| RVT1H470M060747UF50V | Manufacturer: 'DMBJ(振宝佳)' -> 'DMBJ' |
| RVT1H470M060747UF50V | Datasheet: 'https://www.lcsc.com/datasheet/C970679.p' -> 'https://datasheet.lcsc.com/datasheet/pdf/f0a865b841864fb1f67' |
| RVT1H470M060747UF50V | pin 1: '1' -> '+' (datasheet) |
| RVT1H470M060747UF50V | pin 2: '2' -> '-' (datasheet) |
| 100V100UFCD288 | field 'LCSC Part' renamed to 'LCSC' |
| 100V100UFCD288 | Manufacturer: 'HRK(鸿瑞凯电子)' -> 'HRK' |
| 100V100UFCD288 | pin 1: '1' -> '+' (datasheet) |
| 100V100UFCD288 | pin 2: '2' -> '-' (datasheet) |
| TLP290-4 | field 'LCSC Part' renamed to 'LCSC' |
| TLP290-4 | Manufacturer: 'TOSHIBA(东芝)' -> 'TOSHIBA' |
| TLP290-4 | Datasheet: 'https://lcsc.com/product-detail/SMD-Opto' -> 'https://datasheet.lcsc.com/datasheet/pdf/cbe316417a784c8b9ad' |
| TLP290-4 | pin 1: '1' -> 'IN1A' (datasheet) |
| TLP290-4 | pin 2: '2' -> 'IN1B' (datasheet) |
| TLP290-4 | pin 3: '3' -> 'IN2A' (datasheet) |
| TLP290-4 | pin 4: '4' -> 'IN2B' (datasheet) |
| TLP290-4 | pin 5: '5' -> 'IN3A' (datasheet) |
| TLP290-4 | pin 6: '6' -> 'IN3B' (datasheet) |
| TLP290-4 | pin 7: '7' -> 'IN4A' (datasheet) |
| TLP290-4 | pin 8: '8' -> 'IN4B' (datasheet) |
| TLP290-4 | pin 9: '9' -> 'E4' (datasheet) |
| TLP290-4 | pin 10: '10' -> 'C4' (datasheet) |
| TLP290-4 | pin 11: '11' -> 'E3' (datasheet) |
| TLP290-4 | pin 12: '12' -> 'C3' (datasheet) |
| TLP290-4 | pin 13: '13' -> 'E2' (datasheet) |
| TLP290-4 | pin 14: '14' -> 'C2' (datasheet) |
| TLP290-4 | pin 15: '15' -> 'E1' (datasheet) |
| TLP290-4 | pin 16: '16' -> 'C1' (datasheet) |
| KF2EDGR-5.08-3P | field 'LCSC Part' renamed to 'LCSC' |
| KF2EDGR-5.08-3P | Manufacturer: 'KEFA(科发)' -> 'Cixi Kefa Elec' |
| KF2EDGR-5.08-3P | Datasheet: 'https://lcsc.com/product-detail/Pluggabl' -> 'https://datasheet.lcsc.com/datasheet/pdf/50dc2d683fb501b638d' |
| KF2EDGR-5.08-3P | Reference 'CN' -> 'J' |
| 1812L050_30PR | field 'LCSC Part' renamed to 'LCSC' |
| 1812L050_30PR | Manufacturer: 'Littelfuse(美国力特)' -> 'Littelfuse' |
| 1812L050_30PR | Datasheet: 'https://lcsc.com/product-detail/Surface-' -> 'https://datasheet.lcsc.com/datasheet/pdf/f489f06aaead3504c46' |
| 1812L050_30PR | Reference 'F' -> 'RT' |
| 2.54短路帽开口 | field 'LCSC Part' renamed to 'LCSC' |
| 2.54短路帽开口 | Manufacturer: 'BOOMELE(博穆精密)' -> 'BOOMELE(Boom Precision Elec)' |
| 2.54短路帽开口 | Datasheet: 'https://www.lcsc.com/datasheet/C5305.pdf' -> 'https://datasheet.lcsc.com/datasheet/pdf/470ca915a7f249e6997' |
| 2.54短路帽开口 | Reference 'J' -> 'JP' |
| 2.54短路帽开口 | accessory, not on the PCB: 1 placeholder pin(s) and footprint removed, set 'exclude from board' |
| AM26LS32ACDR | field 'LCSC Part' renamed to 'LCSC' |
| AM26LS32ACDR | Manufacturer: 'TI(德州仪器)' -> 'TI' |
| AM26LS32ACDR | Datasheet: 'https://lcsc.com/product-detail/Interfac' -> 'https://datasheet.lcsc.com/datasheet/pdf/5d55aad2b91b4dd6a23' |
| CA-IS3742LN | field 'LCSC Part' renamed to 'LCSC' |
| CA-IS3742LN | Manufacturer: 'Chipanalog(川土微)' -> 'Chipanalog' |
| CA-IS3742LN | Datasheet: 'https://www.lcsc.com/datasheet/C5347249.' -> 'https://datasheet.lcsc.com/datasheet/pdf/a47611d83f8b8be5a05' |
| KF2EDGR-5.08-6P | field 'LCSC Part' renamed to 'LCSC' |
| KF2EDGR-5.08-6P | Manufacturer: 'KEFA(科发)' -> 'Cixi Kefa Elec' |
| KF2EDGR-5.08-6P | Datasheet: 'https://lcsc.com/product-detail/Pluggabl' -> 'https://datasheet.lcsc.com/datasheet/pdf/50dc2d683fb501b638d' |
| KF2EDGR-5.08-6P | Reference 'CN' -> 'J' |
| nSMD025 | field 'LCSC Part' renamed to 'LCSC' |
| nSMD025 | Manufacturer: '台湾陆海' -> 'TECHFUSE' |
| nSMD025 | Datasheet: 'https://lcsc.com/product-detail/Surface-' -> 'https://datasheet.lcsc.com/datasheet/pdf/f635f8e6eef84c3fbd8' |
| nSMD025 | Reference 'F' -> 'RT' |
| PSM712-LF-T7 | field 'LCSC Part' renamed to 'LCSC' |
| PSM712-LF-T7 | Datasheet: 'https://lcsc.com/product-detail/TVS_PSM7' -> 'https://datasheet.lcsc.com/datasheet/pdf/c2ed56a8cad54293a14' |
| PSM712-LF-T7 | pin 1: 'A1' -> 'IO1' (datasheet) |
| PSM712-LF-T7 | pin 3: 'K' -> 'COM' (datasheet) |
| PSM712-LF-T7 | pin 2: 'A1' -> 'IO2' (datasheet) |
| CA-IS3740LN | field 'LCSC Part' renamed to 'LCSC' |
| CA-IS3740LN | Manufacturer: 'Chipanalog(川土微)' -> 'Chipanalog' |
| CA-IS3740LN | Datasheet: 'https://lcsc.com/product-detail/Digital-' -> 'https://datasheet.lcsc.com/datasheet/pdf/a47611d83f8b8be5a05' |
| ULN2803A_C845537 | field 'LCSC Part' renamed to 'LCSC' |
| ULN2803A_C845537 | Manufacturer: 'UMW(友台半导体)' -> 'UMW' |
| ULN2803A_C845537 | Datasheet: 'https://lcsc.com/product-detail/Darlingt' -> 'https://datasheet.lcsc.com/datasheet/pdf/3b624731fce712ad62d' |
| P2R-05P | field 'LCSC Part' renamed to 'LCSC' |
| P2R-05P | Manufacturer: 'OMRON(欧姆龙)' -> 'OMRON' |
| P2R-05P | Datasheet: 'https://www.lcsc.com/datasheet/C1524860.' -> 'https://datasheet.lcsc.com/datasheet/pdf/783bd3e2f3e14ecc6ae' |
| P2R-05P | Reference 'U' -> 'K' |
| P2R-05P | pin 1: '1' -> 'COIL1' (datasheet) |
| P2R-05P | pin 2: '2' -> 'COM' (datasheet) |
| P2R-05P | pin 3: '3' -> 'NO' (datasheet) |
| P2R-05P | pin 4: '4' -> 'NC' (datasheet) |
| P2R-05P | pin 5: '5' -> 'COIL2' (datasheet) |
| CA-IS3740HW | field 'LCSC Part' renamed to 'LCSC' |
| CA-IS3740HW | Manufacturer: 'Chipanalog(川土微)' -> 'Chipanalog' |
| CA-IS3740HW | Datasheet: 'https://lcsc.com/product-detail/Digital-' -> 'https://datasheet.lcsc.com/datasheet/pdf/a47611d83f8b8be5a05' |
| MCP4822-E_SN | field 'LCSC Part' renamed to 'LCSC' |
| MCP4822-E_SN | Manufacturer: 'MICROCHIP(美国微芯)' -> 'MICROCHIP' |
| MCP4822-E_SN | Datasheet: 'https://lcsc.com/product-detail/Digital-' -> 'https://datasheet.lcsc.com/datasheet/pdf/7ef2db3932634fe2abf' |
| LM2904DR | field 'LCSC Part' renamed to 'LCSC' |
| LM2904DR | Manufacturer: 'TI(德州仪器)' -> 'TI' |
| LM2904DR | Datasheet: 'https://lcsc.com/product-detail/General-' -> 'https://datasheet.lcsc.com/datasheet/pdf/5958bf7de8d6439fa00' |
| L78L05ABUTR | field 'LCSC Part' renamed to 'LCSC' |
| L78L05ABUTR | Manufacturer: 'ST(意法半导体)' -> 'ST' |
| L78L05ABUTR | Datasheet: 'https://lcsc.com/product-detail/Linear-V' -> 'https://datasheet.lcsc.com/datasheet/pdf/c5b2ab76554e4a2eb1a' |
| 2N7002DW-7-F | field 'LCSC Part' renamed to 'LCSC' |
| 2N7002DW-7-F | Manufacturer: 'DIODES(美台)' -> 'DIODES' |
| 2N7002DW-7-F | Datasheet: 'https://lcsc.com/product-detail/MOSFET_D' -> 'https://datasheet.lcsc.com/datasheet/pdf/9c1c3e0c83e8857e0ce' |
| SMAJ15A-C148216 | field 'LCSC Part' renamed to 'LCSC' |
| SMAJ15A-C148216 | Manufacturer: 'Littelfuse(美国力特)' -> 'Littelfuse' |
| SMAJ15A-C148216 | Datasheet: 'https://lcsc.com/product-detail/TVS_Litt' -> 'https://datasheet.lcsc.com/datasheet/pdf/bf298e2c0542e0172af' |
| KF2EDGR-5.08-2P | field 'LCSC Part' renamed to 'LCSC' |
| KF2EDGR-5.08-2P | Manufacturer: 'KEFA(科发)' -> 'Cixi Kefa Elec' |
| KF2EDGR-5.08-2P | Datasheet: 'https://lcsc.com/product-detail/Pluggabl' -> 'https://datasheet.lcsc.com/datasheet/pdf/50dc2d683fb501b638d' |
| KF2EDGR-5.08-2P | Reference 'CN' -> 'J' |
| KF2EDGK-5.08-2P-AA | field 'LCSC Part' renamed to 'LCSC' |
| KF2EDGK-5.08-2P-AA | Manufacturer: 'KEFA(科发)' -> 'Cixi Kefa Elec' |
| KF2EDGK-5.08-2P-AA | Datasheet: 'https://www.lcsc.com/datasheet/C440880.p' -> 'https://datasheet.lcsc.com/datasheet/pdf/976c61d45369c406685' |
| KF2EDGK-5.08-2P-AA | Reference 'CN' -> 'P' |
| KF2EDGK-5.08-2P-AA | accessory, not on the PCB: 1 placeholder pin(s) and footprint removed, set 'exclude from board' |
| KF2EDGR-5.08-4P | field 'LCSC Part' renamed to 'LCSC' |
| KF2EDGR-5.08-4P | Manufacturer: 'KEFA(科发)' -> 'Cixi Kefa Elec' |
| KF2EDGR-5.08-4P | Datasheet: 'https://lcsc.com/product-detail/Pluggabl' -> 'https://datasheet.lcsc.com/datasheet/pdf/50dc2d683fb501b638d' |
| KF2EDGR-5.08-4P | Reference 'CN' -> 'J' |
| KF2EDGK-5.08-4P-AA | field 'LCSC Part' renamed to 'LCSC' |
| KF2EDGK-5.08-4P-AA | Manufacturer: 'KEFA(科发)' -> 'Cixi Kefa Elec' |
| KF2EDGK-5.08-4P-AA | Datasheet: 'https://www.lcsc.com/datasheet/C440882.p' -> 'https://datasheet.lcsc.com/datasheet/pdf/976c61d45369c406685' |
| KF2EDGK-5.08-4P-AA | Reference 'CN' -> 'P' |
| KF2EDGK-5.08-4P-AA | accessory, not on the PCB: 1 placeholder pin(s) and footprint removed, set 'exclude from board' |
| STM32F405VGT6 | field 'LCSC Part' renamed to 'LCSC' |
| STM32F405VGT6 | Manufacturer: 'ST(意法半导体)' -> 'ST' |
| STM32F405VGT6 | Datasheet: 'https://lcsc.com/product-detail/ST-Micro' -> 'https://datasheet.lcsc.com/datasheet/pdf/524532d2c17d4323843' |
| 64600001003 | field 'LCSC Part' renamed to 'LCSC' |
| 64600001003 | Manufacturer: 'Littelfuse(美国力特)' -> 'Littelfuse' |
| 64600001003 | Datasheet: 'https://lcsc.com/product-detail/Others_L' -> 'https://datasheet.lcsc.com/datasheet/pdf/4a64479984970992d6e' |
| 64600001003 | Reference 'FH' -> 'F' |
