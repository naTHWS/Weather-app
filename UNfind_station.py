from wetterdienst.provider.dwd.observation import DwdObservationRequest, DwdObservationResolution, DwdObservationParameter, DwdObservationPeriod
import pandas as pd

def get_wuerzburg_station():
    """Findet die DWD Station für Würzburg."""
    request = DwdObservationRequest(
        parameter=DwdObservationParameter.DAILY.TEMPERATURE_AIR_MEAN_200,
        resolution=DwdObservationResolution.DAILY,
        period=DwdObservationPeriod.HISTORICAL
    )
    stations = request.filter_by_name("Würzburg")
    return stations.df

if __name__ == "__main__":
    stations_df = get_wuerzburg_station()
    print(stations_df)
