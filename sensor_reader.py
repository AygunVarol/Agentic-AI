"""Read BME680 sensor. Falls back to simulated data if hardware/lib unavailable."""
import random, time
from datetime import datetime

try:
    import bme680
    _LIB_OK = True
except ImportError:
    _LIB_OK = False

class SensorReader:
    def __init__(self, location: str):
        self.location = location
        if _LIB_OK:
            try:
                self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
            except (RuntimeError, IOError):
                self.sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
            self.sensor.set_humidity_oversample(bme680.OS_2X)
            self.sensor.set_pressure_oversample(bme680.OS_4X)
            self.sensor.set_temperature_oversample(bme680.OS_8X)
            self.sensor.set_filter(bme680.FILTER_SIZE_3)
            self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
            self.sensor.set_gas_heater_temperature(320)
            self.sensor.set_gas_heater_duration(150)
            self.sensor.select_gas_heater_profile(0)
        else:
            self.sensor = None

    def read(self):
        ts = datetime.utcnow().isoformat(timespec='seconds')
        if self.sensor and self.sensor.get_sensor_data():
            data = {
                "timestamp": ts,
                "temperature_C": round(self.sensor.data.temperature, 2),
                "pressure_hPa": round(self.sensor.data.pressure, 2),
                "humidity_pct": round(self.sensor.data.humidity, 2),
                "gas_resistance_ohms": self.sensor.data.gas_resistance if self.sensor.data.heat_stable else None,
                "heat_stable": self.sensor.data.heat_stable,
                "location": self.location,
            }
        else:
            # Simulated fallback
            data = {
                "timestamp": ts,
                "temperature_C": round(random.uniform(18, 30), 2),
                "pressure_hPa": round(random.uniform(980, 1050), 2),
                "humidity_pct": round(random.uniform(30, 70), 2),
                "gas_resistance_ohms": random.randint(10000, 30000),
                "heat_stable": False,
                "location": self.location,
            }
        return data
