#!/bin/bash

set -u

BASE_DIR="data/documents"

mkdir -p \
  "$BASE_DIR/abb" \
  "$BASE_DIR/schneider" \
  "$BASE_DIR/siemens" \
  "$BASE_DIR/oca"

download() {
  url="$1"
  output="$2"

  echo "Downloading: $output"

  curl \
    -fL \
    --retry 3 \
    --retry-delay 2 \
    --connect-timeout 20 \
    "$url" \
    -o "$output" || echo "FAILED: $url"
}

# ABB

download \
"https://library.e.abb.com/public/3ab8247768554d0493e6089883cdec10/Terra%20AC%202.0%20Installation%20manual.pdf" \
"$BASE_DIR/abb/terra-ac-2-installation.pdf"

download \
"https://library.e.abb.com/public/aa65ea5874414dbbac9e46250e1bc9e3/9AKK108472A2654_en_A_Terra%20AC%202.0%20User%20manual.pdf" \
"$BASE_DIR/abb/terra-ac-2-user.pdf"

download \
"https://library.e.abb.com/public/6a169b3d17bb4cb0beb55f9516353e56/Terra%20AC%20User%20manual%20BCM.V3Y00.0-EN%20V004.pdf" \
"$BASE_DIR/abb/terra-ac-user-old.pdf"

download \
"https://library.e.abb.com/public/a8d18e225d11424e8a36703e83f2882b/Terra%20AC%20Manual%20de%20usuario%20_9AKK107992A2148.pdf" \
"$BASE_DIR/abb/terra-ac-user-es.pdf"

download \
"https://library.e.abb.com/public/efe8043609214f2f894d98ed4b7a32da/ABB_brochure_TerraAC_Instruction_A5_220524.pdf" \
"$BASE_DIR/abb/terra-ac-commissioning.pdf"

download \
"https://library.e.abb.com/public/d14b08584fc94724a17bed51eb9b624b/ABB%20Terra%20AC%20Wallbox_Configuration%20Guide%20-%20Solar%20Charging%20Mode_New0317.pdf" \
"$BASE_DIR/abb/terra-ac-configuration.pdf"

download \
"https://library.e.abb.com/public/7ee4db467e25497fa4e34c1719cc0c7f/9AKK107680A6608_BCM.V2M01.0_AA_9AIA017395-0043_Terra%20DC%20Wallbox_Installation_Manual_V1_9.pdf" \
"$BASE_DIR/abb/terra-dc-installation.pdf"

download \
"https://library.e.abb.com/public/4d25f6f89d324252a1c818c035df1ae5/Terra%20DC%20Wallbox%20User%20Manual%20-%20CE%20%26%20UL.pdf" \
"$BASE_DIR/abb/terra-dc-user.pdf"

download \
"https://library.e.abb.com/public/e889d2d78d8b4ce181788211e7e72228/Terra%2094-124-184_CE-Operation%20and%20installation%20manual-EN-Rev.004.pdf" \
"$BASE_DIR/abb/terra-94-124-184-manual.pdf"


# SIEMENS

download \
"https://cache.industry.siemens.com/dl/files/040/109989040/att_1329735/v1/versicharge_wallbox_operating_instructions_en-US_en-US.pdf" \
"$BASE_DIR/siemens/versicharge-wallbox-operating.pdf"

download \
"https://cache.industry.siemens.com/dl/files/039/109989039/att_1329729/v1/versicharge_wallbox_erk_operating_instructions_en-US_en-US.pdf" \
"$BASE_DIR/siemens/versicharge-erk-operating.pdf"

download \
"https://cache.industry.siemens.com/dl/files/709/109977709/att_1330361/v2/SIE-T40011-00-4AUS-Versicharge-48A-Installation-and-Operations-Manual-ES_es-ES.pdf" \
"$BASE_DIR/siemens/versicharge-48a-es.pdf"

download \
"https://cache.industry.siemens.com/dl/files/243/109822243/att_1304512/v1/versicharge_wallbox_compact_instructions_en-US.pdf" \
"$BASE_DIR/siemens/versicharge-compact.pdf"


# OPEN CHARGE ALLIANCE

download \
"https://openchargealliance.org/wp-content/uploads/2023/11/ocpp_1_6_ISO_15118_v10.pdf" \
"$BASE_DIR/oca/ocpp16-iso15118.pdf"

download \
"https://openchargealliance.org/wp-content/uploads/2023/07/new_in_ocpp_201-v10.pdf" \
"$BASE_DIR/oca/ocpp201-whats-new.pdf"

download \
"https://openchargealliance.org/wp-content/uploads/2025/05/OCA-Customizing-OCPP-Implementations.pdf" \
"$BASE_DIR/oca/customizing-ocpp.pdf"

download \
"https://openchargealliance.org/wp-content/uploads/2024/08/improving_uptime_with_ocpp_v1_2.pdf" \
"$BASE_DIR/oca/improving-uptime.pdf"

download \
"https://openchargealliance.org/wp-content/uploads/2025/02/signed_meter_values-v10.pdf" \
"$BASE_DIR/oca/signed-meter-values.pdf"

download \
"https://openchargealliance.org/wp-content/uploads/2026/04/OCPP-Security-Operations-Guide-including-JC-Star.pdf" \
"$BASE_DIR/oca/security-operations-guide.pdf"


echo
echo "Finished."
echo

find "$BASE_DIR" -type f -name "*.pdf" | sort
echo
echo -n "PDF count: "
find "$BASE_DIR" -type f -name "*.pdf" | wc -l
