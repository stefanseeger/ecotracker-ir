"""Sensor platform for Ecotracker integration."""

from __future__ import annotations

from datetime import timedelta, date, datetime
import logging

import aiohttp
import async_timeout

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_IP_ADDRESS,
    UnitOfPower,
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 5
API_RESPONSE_JSON_KEYS = [
    "power",
    "powerPhase1",
    "powerPhase2",
    "powerPhase3",
    "powerAvg",
    "energyCounterIn",
    "energyCounterOut",
]

API_ENDPOINT = "/v1/json"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ecotracker sensors based on a config entry."""
    ip_address = entry.data[CONF_IP_ADDRESS]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    url = f"http://{ip_address}{API_ENDPOINT}"

    session = async_get_clientsession(hass)
    coordinator = EcotrackerCoordinator(hass, session, url, scan_interval)

    await coordinator.async_config_entry_first_refresh()

    entities = [
        EcotrackerPowerSensor(coordinator, entry),
        EcotrackerPowerPhase1Sensor(coordinator, entry),
        EcotrackerPowerPhase2Sensor(coordinator, entry),
        EcotrackerPowerPhase3Sensor(coordinator, entry),
        EcotrackerPowerAvgSensor(coordinator, entry),
        EcotrackerEnergyInSensor(coordinator, entry),
        EcotrackerEnergyOutSensor(coordinator, entry),
        EcotrackerDailyEnergyInSensor(coordinator, entry),
        EcotrackerDailyEnergyOutSensor(coordinator, entry),
        EcotrackerMonthlyEnergyInSensor(coordinator, entry),
        EcotrackerMonthlyEnergyOutSensor(coordinator, entry),
        EcotrackerYearlyEnergyInSensor(coordinator, entry),
        EcotrackerYearlyEnergyOutSensor(coordinator, entry),
    ]

    async_add_entities(entities)


class EcotrackerCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Ecotracker data."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        url: str,
        scan_interval: int,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.session = session
        self.url = url

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(self.url) as response:
                    if response.status != 200:
                        raise UpdateFailed(
                            f"Error fetching data: HTTP {response.status}"
                        )
                    data = await response.json()

                    if not all(key in data for key in API_RESPONSE_JSON_KEYS):
                        raise UpdateFailed("Missing required keys in response")

                    return data
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err


class EcotrackerSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Ecotracker sensors."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Ecotracker",
            manufacturer="Ecotracker",
            model="Energy Monitor",
        )


class EcotrackerPowerSensor(EcotrackerSensorBase):
    """Representation of Ecotracker Power Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "power"
        self._attr_unique_id = f"{entry.entry_id}_power"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("power")


class EcotrackerPowerPhase1Sensor(EcotrackerSensorBase):
    """Representation of Ecotracker Power Phase 1 Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "power_phase_1"
        self._attr_unique_id = f"{entry.entry_id}_power_phase1"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("powerPhase1")


class EcotrackerPowerPhase2Sensor(EcotrackerSensorBase):
    """Representation of Ecotracker Power Phase 2 Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "power_phase_2"
        self._attr_unique_id = f"{entry.entry_id}_power_phase2"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("powerPhase2")


class EcotrackerPowerPhase3Sensor(EcotrackerSensorBase):
    """Representation of Ecotracker Power Phase 3 Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "power_phase_3"
        self._attr_unique_id = f"{entry.entry_id}_power_phase3"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("powerPhase3")


class EcotrackerPowerAvgSensor(EcotrackerSensorBase):
    """Representation of Ecotracker Power Average Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "power_avg"
        self._attr_unique_id = f"{entry.entry_id}_power_avg"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("powerAvg")


class EcotrackerEnergyInSensor(EcotrackerSensorBase):
    """Representation of Ecotracker Energy Counter In Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "energy_in"
        self._attr_unique_id = f"{entry.entry_id}_energy_in"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("energyCounterIn")


class EcotrackerEnergyOutSensor(EcotrackerSensorBase):
    """Representation of Ecotracker Energy Counter Out Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "energy_out"
        self._attr_unique_id = f"{entry.entry_id}_energy_out"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("energyCounterOut")


class EcotrackerDailyEnergyInSensor(EcotrackerSensorBase):
    """Representation of Ecotracker Daily Energy In Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "daily_energy_in"
        self._attr_unique_id = f"{entry.entry_id}_daily_energy_in"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
        self._last_reset = date.today()
        self._last_energy_in = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        current_energy_in = self.coordinator.data.get("energyCounterIn")

        # Reset if we've moved to a new day
        if date.today() != self._last_reset:
            self._last_reset = date.today()
            self._last_energy_in = current_energy_in
            return 0

        # First time initialization
        if self._last_energy_in is None:
            self._last_energy_in = current_energy_in
            return 0

        # Calculate the difference
        if current_energy_in is not None and self._last_energy_in is not None:
            daily_energy = current_energy_in - self._last_energy_in
            # Ensure we don't return negative values
            return max(0, daily_energy)

        return 0


class EcotrackerDailyEnergyOutSensor(EcotrackerSensorBase):
    """Representation of Ecotracker Daily Energy Out Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "daily_energy_out"
        self._attr_unique_id = f"{entry.entry_id}_daily_energy_out"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
        self._last_reset = date.today()
        self._last_energy_out = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        current_energy_out = self.coordinator.data.get("energyCounterOut")

        # Reset if we've moved to a new day
        if date.today() != self._last_reset:
            self._last_reset = date.today()
            self._last_energy_out = current_energy_out
            return 0

        # First time initialization
        if self._last_energy_out is None:
            self._last_energy_out = current_energy_out
            return 0

        # Calculate the difference
        if current_energy_out is not None and self._last_energy_out is not None:
            daily_energy = current_energy_out - self._last_energy_out
            # Ensure we don't return negative values
            return max(0, daily_energy)

        return 0


class EcotrackerMonthlyEnergyInSensor(EcotrackerSensorBase):
    """Representation of Ecotracker Monthly Energy In Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "monthly_energy_in"
        self._attr_unique_id = f"{entry.entry_id}_monthly_energy_in"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
        self._last_reset = (date.today().year, date.today().month)
        self._last_energy_in = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        current_energy_in = self.coordinator.data.get("energyCounterIn")
        current_month = (date.today().year, date.today().month)

        # Reset if we've moved to a new month
        if current_month != self._last_reset:
            self._last_reset = current_month
            self._last_energy_in = current_energy_in
            return 0

        # First time initialization
        if self._last_energy_in is None:
            self._last_energy_in = current_energy_in
            return 0

        # Calculate the difference
        if current_energy_in is not None and self._last_energy_in is not None:
            monthly_energy = current_energy_in - self._last_energy_in
            # Ensure we don't return negative values
            return max(0, monthly_energy)

        return 0


class EcotrackerMonthlyEnergyOutSensor(EcotrackerSensorBase):
    """Representation of Ecotracker Monthly Energy Out Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "monthly_energy_out"
        self._attr_unique_id = f"{entry.entry_id}_monthly_energy_out"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
        self._last_reset = (date.today().year, date.today().month)
        self._last_energy_out = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        current_energy_out = self.coordinator.data.get("energyCounterOut")
        current_month = (date.today().year, date.today().month)

        # Reset if we've moved to a new month
        if current_month != self._last_reset:
            self._last_reset = current_month
            self._last_energy_out = current_energy_out
            return 0

        # First time initialization
        if self._last_energy_out is None:
            self._last_energy_out = current_energy_out
            return 0

        # Calculate the difference
        if current_energy_out is not None and self._last_energy_out is not None:
            monthly_energy = current_energy_out - self._last_energy_out
            # Ensure we don't return negative values
            return max(0, monthly_energy)

        return 0


class EcotrackerYearlyEnergyInSensor(EcotrackerSensorBase):
    """Representation of Ecotracker Yearly Energy In Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "yearly_energy_in"
        self._attr_unique_id = f"{entry.entry_id}_yearly_energy_in"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
        self._last_reset = date.today().year
        self._last_energy_in = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        current_energy_in = self.coordinator.data.get("energyCounterIn")
        current_year = date.today().year

        # Reset if we've moved to a new year
        if current_year != self._last_reset:
            self._last_reset = current_year
            self._last_energy_in = current_energy_in
            return 0

        # First time initialization
        if self._last_energy_in is None:
            self._last_energy_in = current_energy_in
            return 0

        # Calculate the difference
        if current_energy_in is not None and self._last_energy_in is not None:
            yearly_energy = current_energy_in - self._last_energy_in
            # Ensure we don't return negative values
            return max(0, yearly_energy)

        return 0


class EcotrackerYearlyEnergyOutSensor(EcotrackerSensorBase):
    """Representation of Ecotracker Yearly Energy Out Sensor."""

    def __init__(self, coordinator: EcotrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_translation_key = "yearly_energy_out"
        self._attr_unique_id = f"{entry.entry_id}_yearly_energy_out"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
        self._last_reset = date.today().year
        self._last_energy_out = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        current_energy_out = self.coordinator.data.get("energyCounterOut")
        current_year = date.today().year

        # Reset if we've moved to a new year
        if current_year != self._last_reset:
            self._last_reset = current_year
            self._last_energy_out = current_energy_out
            return 0

        # First time initialization
        if self._last_energy_out is None:
            self._last_energy_out = current_energy_out
            return 0

        # Calculate the difference
        if current_energy_out is not None and self._last_energy_out is not None:
            yearly_energy = current_energy_out - self._last_energy_out
            # Ensure we don't return negative values
            return max(0, yearly_energy)

        return 0
