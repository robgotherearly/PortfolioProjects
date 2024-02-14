SELECT *
FROM PortfolioProject..CovidDeaths$
WHERE continent is not null
ORDER BY 3,4

SELECT * 
FROM PortfolioProject..CovidVaccinations$
ORDER BY 3,4

--Select data that we are going to be using
SELECT Location,date,total_cases,new_cases,total_deaths,population
FROM PortfolioProject..CovidDeaths$
WHERE continent is not null
ORDER BY 1,2

--Looking at Total Cases vs Total Deaths
--Shows likelihood of dying if you contract covid in your country 
SELECT Location,date,total_cases,total_deaths,(total_deaths/total_cases) * 100 AS DeathPercentage
FROM PortfolioProject..CovidDeaths$
WHERE Location like '%Ghana%'
and continent is not null
ORDER BY 1,2

--Looking at Total Cases vs Population
--Shows what percentage of the Population has got Covid
SELECT Location,date,Population,total_cases,(total_cases/population) * 100 AS PercentagePopulationInfected
FROM PortfolioProject..CovidDeaths$
--WHERE Location like '%Ghana%'
WHERE continent is not null
ORDER BY 1,2

--Looking at Countries with Highest Infection Rate compared to Population
SELECT Location,Population,MAX(total_cases) AS HighestInfectionCount,max((total_cases/population)) * 100 AS PercentagePopulationInfected
FROM PortfolioProject..CovidDeaths$
--WHERE Location like '%Ghana%'
WHERE continent is not null
GROUP BY Location,Population
ORDER BY PercentagePopulationInfected DESC

--Showing the Countries with the Highest Death Count Per Population
SELECT Location,MAX(CAST (total_deaths AS INT)) AS TotalDeathCount
FROM PortfolioProject..CovidDeaths$
--WHERE Location like '%Ghana%'
WHERE continent is not null
GROUP BY Location
ORDER BY TotalDeathCount DESC

--Let's break things down by continent


--Showing continents with the Highest Death Count Per Population
SELECT continent,MAX(CAST (total_deaths AS INT)) AS TotalDeathCount
FROM PortfolioProject..CovidDeaths$
--WHERE Location like '%Ghana%'
WHERE continent is not null
GROUP BY continent
ORDER BY TotalDeathCount DESC

--GLOBAL NUMBERS
SELECT DATE,SUM(new_cases) AS total_cases, SUM(CAST(new_deaths AS INT)) AS total_deaths, SUM(CAST(new_deaths AS INT))/ SUM
(new_cases) * 100 AS DeathPercentage
FROM PortfolioProject..CovidDeaths$
--WHERE Location like '%states%'
WHERE continent is not null
GROUP BY DATE
ORDER BY 1,2


--Total Cases Globally
SELECT SUM(new_cases) AS total_cases, SUM(CAST(new_deaths AS INT)) AS total_deaths, SUM(CAST(new_deaths AS INT))/ SUM
(new_cases) * 100 AS DeathPercentage
FROM PortfolioProject..CovidDeaths$
--WHERE Location like '%states%'
WHERE continent is not null
--GROUP BY DATE
ORDER BY 1,2


--Looking at Total Population vs Vaccination
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations,
SUM(CONVERT(INT,vac.new_vaccinations)) OVER (PARTITION BY dea.location ORDER BY dea.location,
dea.date) AS RollingPeopleVaccinated
--, (RollingPeopleVaccinated/population)*100
FROM PortfolioProject..CovidDeaths$ dea
JOIN PortfolioProject..CovidVaccinations$ vac
	ON dea.location = vac.location
	AND dea.date = vac.date
WHERE dea.continent IS NOT NULL
ORDER BY 2,3


-- USE CTE

WITH PopvsVac (Continent, Location, Date, Population, New_Vaccinations, RollingPeopleVaccinated)
AS
(
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations,
SUM(CONVERT(INT,vac.new_vaccinations)) OVER (PARTITION BY dea.location ORDER BY dea.location,
dea.date) AS RollingPeopleVaccinated
--, (RollingPeopleVaccinated/population)*100
FROM PortfolioProject..CovidDeaths$ dea
JOIN PortfolioProject..CovidVaccinations$ vac
	ON dea.location = vac.location
	AND dea.date = vac.date
WHERE dea.continent IS NOT NULL
--ORDER BY 2,3
)

SELECT * ,(RollingPeopleVaccinated/Population) * 100
FROM PopvsVac 


--TEMP TABLE

CREATE TABLE #PercentPopulationVaccinated
(
Continent NVARCHAR (255),
Location NVARCHAR (255),
DATE DATETIME,
POPULATION NUMERIC,
New_Vaccination NUMERIC,
RollingPeopleVaccinated NUMERIC,
)

INSERT INTO #PercentPopulationVaccinated
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations,
SUM(CONVERT(INT,vac.new_vaccinations)) OVER (PARTITION BY dea.location ORDER BY dea.location,
dea.date) AS RollingPeopleVaccinated
--, (RollingPeopleVaccinated/population)*100
FROM PortfolioProject..CovidDeaths$ dea
JOIN PortfolioProject..CovidVaccinations$ vac
	ON dea.location = vac.location
	AND dea.date = vac.date
WHERE dea.continent IS NOT NULL
--ORDER BY 2,3

SELECT * ,(RollingPeopleVaccinated/Population) * 100
FROM #PercentPopulationVaccinated


-- Creating view to store data for later visualizations

CREATE VIEW PercentPoulationVaccinated AS

(Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations,
SUM(CONVERT(INT,vac.new_vaccinations)) OVER (PARTITION BY dea.location ORDER BY dea.location,
dea.date) AS RollingPeopleVaccinated
--, (RollingPeopleVaccinated/population)*100
FROM PortfolioProject..CovidDeaths$ dea
JOIN PortfolioProject..CovidVaccinations$ vac
	ON dea.location = vac.location
	AND dea.date = vac.date
WHERE dea.continent IS NOT NULL)

SELECT *
FROM * PercentPopulationVaccinated

--43:48


