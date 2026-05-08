# 🗂️ Schémas SQL Server legacy — GestionCardex

**Source** : 3 dumps SSMS (Schema Only).
**Encodage original** : UTF-16 LE.

| Base | Rôle | Tables |
|------|------|--------|
| `sCardAvo` | BDD principale (avocats, adresses, mandats) | 19 |
| `sStaticPc` | Tables de référence (codes, listes, paramètres) | 84 |
| `sArt52` | Article 52 — paiements et règlements | 126 |

## 🎯 Mapping vers le modèle MongoDB actuel

| Table SQL Server | Statut | Cible MongoDB |
|------------------|--------|---------------|
| `Avocats` | ✅ migré | MongoDB collection `avocats` (server.py AvocatBase / AvocatOut) |
| `Adresses` | ✅ migré | MongoDB collection `avocat_adresses` + champ embarqué `adresse` sur l'avocat courant |
| `infomega` | ✅ migré | MongoDB collection `avocat_mega` (profil méga) |
| `inhpra` | ✅ migré | MongoDB collection `avocat_inhab` (périodes d'inhabilité) |
| `infodistrict` | ✅ migré | MongoDB collection `avocat_mega.districts` (tableau d'IDs) |
| `Settings` | ✅ migré | Variables d'environnement / collection `connexions` |

Toutes les autres tables (registres financiers, journaux, etc.) ne sont pas encore migrées —
elles seront ajoutées progressivement selon le besoin métier.

---

## 📦 Base `sCardAvo`

**19 tables détectées.**

### `Adresses` 🎯

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(6)` | ✗ |  |
| `adresse` | `varchar(100)` | ✓ |  |
| `ville` | `varchar(40)` | ✓ |  |
| `province` | `varchar(20)` | ✓ |  |
| `codepostal` | `char(7)` | ✓ |  |
| `telephone` | `char(15)` | ✓ |  |
| `telephone2` | `char(15)` | ✓ |  |
| `fax` | `char(15)` | ✓ |  |
| `adremail` | `varchar(50)` | ✓ |  |
| `noseq` | `int` | ✓ |  |
| `adresse2` | `varchar(30)` | ✓ |  |
| `adresse3` | `varchar(30)` | ✓ |  |
| `courant` | `char(1)` | ✓ |  |
| `dateadr` | `smalldatetime` | ✓ |  |
| `poste1` | `char(6)` | ✓ |  |
| `poste2` | `char(6)` | ✓ |  |
| `RowId` | `uniqueidentifier` | ✗ | 🔑 |
| `usermodif` | `varchar(20)` | ✓ |  |
| `datemodif` | `datetime` | ✓ |  |

### `Fournisseurs`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `Type` | `char(6)` | ✓ |  |
| `NoId` | `char(10)` | ✓ |  |
| `Nas` | `char(9)` | ✓ |  |
| `Nom1` | `varchar(30)` | ✓ |  |
| `Nom2` | `varchar(30)` | ✓ |  |
| `Adresse1` | `varchar(60)` | ✓ |  |
| `Adresse2` | `varchar(60)` | ✓ |  |
| `Adresse3` | `varchar(60)` | ✓ |  |
| `Ville` | `varchar(30)` | ✓ |  |
| `Province` | `varchar(20)` | ✓ |  |
| `CodePostal` | `char(6)` | ✓ |  |
| `Annee` | `char(4)` | ✓ |  |
| `Paiement` | `decimal(15, 2)` | ✓ |  |
| `Commentaire` | `varchar(500)` | ✓ |  |

### `Avocats` 🎯

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(6)` | ✗ | 🔑 |
| `sectbar` | `varchar(100)` | ✓ |  |
| `mega` | `char(1)` | ✓ |  |
| `nom` | `varchar(50)` | ✗ |  |
| `prenom` | `varchar(50)` | ✗ |  |
| `actpass` | `char(1)` | ✗ |  |
| `dateinscbarr` | `char(10)` | ✓ |  |
| `payable` | `char(1)` | ✓ |  |
| `adrcour` | `int` | ✓ |  |
| `adrnonpay` | `int` | ✓ |  |
| `codebar` | `char(10)` | ✓ |  |
| `comm` | `varchar(500)` | ✓ |  |
| `datemodif` | `smalldatetime` | ✓ |  |
| `nas` | `char(9)` | ✓ |  |
| `depodirect` | `char(1)` | ✓ |  |
| `codeusager` | `char(6)` | ✓ |  |
| `motpasse1` | `char(8)` | ✓ |  |
| `motpasse2` | `char(8)` | ✓ |  |
| `factweb` | `char(1)` | ✓ |  |
| `confweb` | `char(1)` | ✓ |  |
| `villeref` | `varchar(40)` | ✓ |  |
| `usermodif` | `varchar(20)` | ✓ |  |
| `surveil` | `char(1)` | ✗ |  |
| `neq` | `char(10)` | ✓ |  |

### `_Fourniseurs_TODELETE`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `Type` | `varchar(50)` | ✓ |  |
| `NoId` | `varchar(50)` | ✓ |  |
| `NAS` | `varchar(50)` | ✓ |  |
| `Nom1` | `varchar(50)` | ✓ |  |
| `Nom2` | `varchar(50)` | ✓ |  |
| `Adresse1` | `varchar(50)` | ✓ |  |
| `Adresse2` | `varchar(50)` | ✓ |  |
| `Adresse3` | `varchar(50)` | ✓ |  |
| `Ville` | `varchar(50)` | ✓ |  |
| `Province` | `varchar(50)` | ✓ |  |
| `CodePostal` | `varchar(50)` | ✓ |  |
| `Annee` | `varchar(50)` | ✓ |  |
| `Paiement` | `varchar(50)` | ✓ |  |

### `codemtl`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(6)` | ✗ |  |
| `codeMtl` | `char(6)` | ✓ |  |
| `codelaur` | `char(6)` | ✓ |  |

### `Fournisseurs_2023`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `Type` | `char(6)` | ✓ |  |
| `NoId` | `char(10)` | ✓ |  |
| `Nas` | `char(9)` | ✓ |  |
| `Nom1` | `varchar(30)` | ✓ |  |
| `Nom2` | `varchar(30)` | ✓ |  |
| `Adresse1` | `varchar(60)` | ✓ |  |
| `Adresse2` | `varchar(60)` | ✓ |  |
| `Adresse3` | `varchar(60)` | ✓ |  |
| `Ville` | `varchar(30)` | ✓ |  |
| `Province` | `varchar(20)` | ✓ |  |
| `CodePostal` | `char(6)` | ✓ |  |
| `Annee` | `char(4)` | ✓ |  |
| `Paiement` | `decimal(15, 2)` | ✓ |  |
| `Commentaire` | `varchar(500)` | ✓ |  |

### `FviLog`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `codeavo` | `char(6)` | ✗ |  |
| `nomavo` | `varchar(100)` | ✗ |  |
| `dateappel` | `smalldatetime` | ✗ |  |
| `raison` | `varchar(30)` | ✗ |  |
| `commentaire` | `varchar(max)` | ✗ |  |
| `regle` | `char(1)` | ✗ |  |

### `FviPmj`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `iUpdateID` | `int` | ✓ |  |
| `cDatabase` | `nvarchar(15)` | ✓ |  |
| `cTable` | `nvarchar(15)` | ✓ |  |
| `cCle` | `nvarchar(255)` | ✓ |  |
| `cAction` | `nvarchar(1)` | ✓ |  |
| `dModif` | `smalldatetime` | ✓ |  |

### `infodistrict` 🎯

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(6)` | ✗ |  |
| `nodist` | `int` | ✗ |  |

### `infomega` 🎯

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(6)` | ✗ |  |
| `francais` | `char(1)` | ✗ |  |
| `anglais` | `char(1)` | ✗ |  |
| `autres` | `char(40)` | ✗ |  |
| `experience` | `int` | ✗ |  |
| `details` | `varchar(500)` | ✗ |  |
| `mega` | `char(1)` | ✗ |  |
| `tarification` | `char(1)` | ✗ |  |
| `art486` | `char(1)` | ✗ |  |
| `art672` | `char(1)` | ✗ |  |
| `art684` | `char(1)` | ✗ |  |
| `districthab` | `char(100)` | ✗ |  |
| `commentaire` | `varchar(5000)` | ✗ |  |
| `dateinsc` | `datetime` | ✗ |  |
| `usermodif` | `char(20)` | ✗ |  |
| `datemodif` | `datetime` | ✓ |  |
| `sectbar` | `varchar(100)` | ✓ |  |

### `inhpra` 🎯

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(6)` | ✗ |  |
| `datedeb` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✗ |  |
| `comm` | `text` | ✓ |  |
| `Id` | `int` | ✓ |  |

### `lettremega`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `codeavo` | `nvarchar(255)` | ✗ |  |
| `dateenvoi` | `datetime` | ✗ |  |
| `datereception` | `datetime` | ✓ |  |

### `Settings` 🎯

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `Id` | `int` | ✓ |  |
| `Name` | `nvarchar(50)` | ✗ |  |
| `Value` | `nvarchar(50)` | ✓ |  |

### `Sommaire$`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `nvarchar(2550)` | ✓ |  |
| `nom2` | `nvarchar(2550)` | ✓ |  |
| `adresse` | `nvarchar(2550)` | ✓ |  |
| `adresse2` | `nvarchar(2550)` | ✓ |  |
| `ville` | `nvarchar(255)` | ✓ |  |
| `codepostal` | `nvarchar(255)` | ✓ |  |
| `type` | `float` | ✓ |  |
| `nas` | `nvarchar(255)` | ✓ |  |
| `neq` | `float` | ✓ |  |
| `total` | `float` | ✓ |  |

### `Sommaire2020$`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `NOM DU FOURNISSEUR` | `nvarchar(255)` | ✓ |  |
| `adresse1` | `nvarchar(255)` | ✓ |  |
| `adresse2` | `nvarchar(255)` | ✓ |  |
| `adresse3` | `nvarchar(255)` | ✓ |  |
| `F5` | `nvarchar(255)` | ✓ |  |
| `ville` | `nvarchar(255)` | ✓ |  |
| `codepostal` | `nvarchar(255)` | ✓ |  |
| `Forme juridique` | `float` | ✓ |  |
| `NAS` | `float` | ✓ |  |
| `No TVQ` | `float` | ✓ |  |
| `$ MONTANT TOTAL POUR LE RELEVÉ 27 *` | `float` | ✓ |  |

### `tAvocatsErreurMigration`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `cArt52uid` | `varchar(10)` | ✗ |  |
| `NbPieces` | `int` | ✓ |  |

### `tRev27_Config`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `Annee` | `int` | ✗ | 🔑 |
| `NoAutorisation` | `varchar(25)` | ✓ |  |
| `NoCertification` | `varchar(25)` | ✓ |  |
| `NoPreparateur` | `varchar(50)` | ✓ |  |
| `NomPreparateur` | `varchar(500)` | ✓ |  |
| `Compagnie` | `varchar(500)` | ✓ |  |
| `Adresse1` | `varchar(500)` | ✓ |  |
| `Adresse2` | `varchar(500)` | ✓ |  |
| `Ville` | `varchar(500)` | ✓ |  |
| `Province` | `varchar(50)` | ✓ |  |
| `CodePostal` | `varchar(6)` | ✓ |  |
| `NomTI` | `varchar(500)` | ✓ |  |
| `TelTI` | `varchar(50)` | ✓ |  |
| `TelPosteTI` | `varchar(50)` | ✓ |  |
| `NomCompta` | `varchar(500)` | ✓ |  |
| `TelCompta` | `varchar(50)` | ✓ |  |
| `TelPosteCompta` | `varchar(50)` | ✓ |  |
| `CourrielRespon` | `varchar(50)` | ✓ |  |
| `IdPartenaireReleves` | `varchar(50)` | ✓ |  |
| `IdProduitReleves` | `varchar(50)` | ✓ |  |
| `NoXMLDebut` | `varchar(50)` | ✓ |  |
| `NoXMLFin` | `varchar(50)` | ✓ |  |
| `NoXMLDispo` | `varchar(50)` | ✓ |  |
| `NoReleveDebut` | `varchar(50)` | ✓ |  |
| `NoReleveFin` | `varchar(50)` | ✓ |  |
| `NoReleveDispo` | `varchar(50)` | ✓ |  |
| `RepertoireRev` | `varchar(75)` | ✓ |  |
| `DateC` | `datetime` | ✓ |  |
| `DateM` | `datetime` | ✓ |  |

### `tRev27_Contrib`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `ContriID` | `int` | ✓ | 🔑 |
| `Annee` | `int` | ✓ |  |
| `Type` | `int` | ✓ |  |
| `NAS` | `varchar(9)` | ✓ |  |
| `NomFam` | `varchar(250)` | ✓ |  |
| `Prenom` | `varchar(250)` | ✓ |  |
| `Initial` | `varchar(50)` | ✓ |  |
| `NoId` | `varchar(10)` | ✓ |  |
| `CodeAvo` | `varchar(10)` | ✓ |  |
| `NEQ` | `varchar(10)` | ✓ |  |
| `Nom1` | `varchar(500)` | ✓ |  |
| `Nom2` | `varchar(500)` | ✓ |  |
| `Adresse1` | `varchar(500)` | ✓ |  |
| `Adresse2` | `varchar(500)` | ✓ |  |
| `Ville` | `varchar(500)` | ✓ |  |
| `Province` | `varchar(5)` | ✓ |  |
| `CodePostal` | `varchar(10)` | ✓ |  |
| `Montant` | `numeric(18, 2)` | ✓ |  |
| `NoReleveXML` | `varchar(20)` | ✓ |  |
| `TypeEnvoieXML` | `char(1)` | ✓ |  |
| `NoReveleXMLLast` | `varchar(20)` | ✓ |  |
| `TypeReleve` | `char(1)` | ✓ |  |
| `NoReleve` | `varchar(50)` | ✓ |  |
| `DateEnvoieXML` | `datetime` | ✓ |  |
| `FaitReleve` | `bit` | ✓ |  |

### `tRev27_ContribHisto`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `ContriID` | `int` | ✗ |  |
| `Annee` | `int` | ✓ |  |
| `Type` | `int` | ✓ |  |
| `NAS` | `varchar(9)` | ✓ |  |
| `NomFam` | `varchar(250)` | ✓ |  |
| `Prenom` | `varchar(250)` | ✓ |  |
| `Initial` | `varchar(50)` | ✓ |  |
| `NoId` | `varchar(10)` | ✓ |  |
| `CodeAvo` | `varchar(10)` | ✓ |  |
| `NEQ` | `varchar(10)` | ✓ |  |
| `Nom1` | `varchar(500)` | ✓ |  |
| `Nom2` | `varchar(500)` | ✓ |  |
| `Adresse1` | `varchar(500)` | ✓ |  |
| `Adresse2` | `varchar(500)` | ✓ |  |
| `Ville` | `varchar(500)` | ✓ |  |
| `Province` | `varchar(5)` | ✓ |  |
| `CodePostal` | `varchar(10)` | ✓ |  |
| `Montant` | `numeric(18, 2)` | ✓ |  |
| `NoReleveXML` | `varchar(20)` | ✓ |  |
| `TypeEnvoieXML` | `char(1)` | ✓ |  |
| `NoReveleXMLLast` | `varchar(20)` | ✓ |  |
| `TypeReleve` | `char(1)` | ✓ |  |
| `NoReleve` | `varchar(50)` | ✓ |  |
| `DateEnvoieXML` | `datetime` | ✓ |  |
| `FaitReleve` | `bit` | ✓ |  |

---

## 📦 Base `sStaticPc`

**84 tables détectées.**

### `BaremeVolet`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `NoCateg` | `int` | ✗ |  |
| `DateDebut` | `smalldatetime` | ✗ |  |
| `DateFin` | `smalldatetime` | ✓ |  |
| `Seuil` | `int` | ✓ |  |
| `Volet0` | `int` | ✓ |  |
| `Volet100` | `int` | ✓ |  |
| `Volet200` | `int` | ✓ |  |
| `Volet300` | `int` | ✓ |  |
| `Volet400` | `int` | ✓ |  |
| `Volet500` | `int` | ✓ |  |
| `Volet600` | `int` | ✓ |  |
| `Volet700` | `int` | ✓ |  |
| `Volet800` | `int` | ✓ |  |

### `oldnatures`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(5)` | ✓ |  |
| `categorie` | `char(40)` | ✓ |  |
| `description` | `char(61)` | ✓ |  |
| `descang` | `char(90)` | ✓ |  |
| `natnommcouv` | `decimal(1, 0)` | ✓ |  |
| `natinactif` | `decimal(1, 0)` | ✓ |  |
| `natgra001` | `char(2)` | ✓ |  |
| `natgra002` | `char(2)` | ✓ |  |
| `natgra003` | `char(2)` | ✓ |  |
| `natgra004` | `char(2)` | ✓ |  |
| `service` | `char(31)` | ✓ |  |

### `natures`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(5)` | ✓ |  |
| `categorie` | `char(40)` | ✓ |  |
| `description` | `char(70)` | ✓ |  |
| `descang` | `char(70)` | ✓ |  |
| `natnommcouv` | `decimal(1, 0)` | ✓ |  |
| `natinactif` | `decimal(1, 0)` | ✓ |  |
| `natgra001` | `char(2)` | ✓ |  |
| `natgra002` | `char(2)` | ✓ |  |
| `natgra003` | `char(2)` | ✓ |  |
| `natgra004` | `char(2)` | ✓ |  |
| `service` | `char(31)` | ✓ |  |

### `natserv`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(1)` | ✓ |  |
| `description` | `char(60)` | ✓ |  |
| `descang` | `char(60)` | ✓ |  |
| `Ponderation` | `numeric(4, 2)` | ✓ |  |

### `boite`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `noreg` | `char(2)` | ✓ |  |
| `lecture` | `char(35)` | ✓ |  |
| `periodeduau` | `char(25)` | ✓ |  |
| `tottraitevcvg` | `int` | ✓ |  |
| `totrefusvcvg` | `int` | ✓ |  |
| `attregarvcvg` | `int` | ✓ |  |
| `attconarvcvg` | `int` | ✓ |  |
| `attregppvcvg` | `int` | ✓ |  |
| `attconppvcvg` | `int` | ✓ |  |
| `tottraitevc` | `int` | ✓ |  |
| `totrefusvc` | `int` | ✓ |  |
| `attregarvc` | `int` | ✓ |  |
| `attconarvc` | `int` | ✓ |  |
| `attregppvc` | `int` | ✓ |  |
| `attconppvc` | `int` | ✓ |  |
| `cle` | `varchar(35)` | ✓ |  |
| `projet` | `varchar(10)` | ✓ |  |
| `vcvg` | `varchar(4)` | ✓ |  |
| `Traite` | `int` | ✓ |  |
| `Refus` | `int` | ✓ |  |
| `AttRegPerm` | `int` | ✓ |  |
| `AttCondPerm` | `int` | ✓ |  |
| `AttRegPriv` | `int` | ✓ |  |
| `AttCondPriv` | `int` | ✓ |  |
| `noseq` | `int` | ✓ |  |

### `ProvCa`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `ProvId` | `uniqueidentifier` | ✗ |  |
| `Code` | `nchar(4)` | ✓ |  |
| `DescFr` | `nvarchar(100)` | ✓ |  |
| `DescAn` | `nvarchar(100)` | ✓ |  |

### `regions`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(4)` | ✓ |  |
| `description` | `char(25)` | ✓ |  |

### `activite`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(15)` | ✓ |  |
| `description` | `char(25)` | ✓ |  |

### `anneeFiscale`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `annee` | `numeric(18, 0)` | ✓ |  |
| `statut` | `bit` | ✓ |  |
| `detail` | `char(9)` | ✓ |  |
| `datemodif` | `datetime` | ✓ |  |

### `archi_natcateg`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✓ |  |
| `description` | `char(40)` | ✓ |  |
| `descang` | `char(40)` | ✓ |  |

### `archi_natgr002`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✓ |  |
| `description` | `char(25)` | ✓ |  |
| `descFVI` | `varchar(25)` | ✓ |  |
| `descang` | `char(25)` | ✓ |  |

### `archi_natserv`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(1)` | ✓ |  |
| `description` | `char(60)` | ✓ |  |
| `descang` | `char(60)` | ✓ |  |

### `archi_natures`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(5)` | ✓ |  |
| `categorie` | `char(40)` | ✓ |  |
| `description` | `char(70)` | ✓ |  |
| `descang` | `char(70)` | ✓ |  |
| `natnommcouv` | `decimal(1, 0)` | ✓ |  |
| `natinactif` | `decimal(1, 0)` | ✓ |  |
| `natgra001` | `char(2)` | ✓ |  |
| `natgra002` | `char(2)` | ✓ |  |
| `natgra003` | `char(2)` | ✓ |  |
| `natgra004` | `char(2)` | ✓ |  |
| `service` | `char(31)` | ✓ |  |

### `avispaie`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `typepaiement` | `char(20)` | ✗ |  |
| `description` | `char(175)` | ✗ |  |

### `BaremeCalcul`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `RegEloiMulti` | `real` | ✓ |  |
| `DeducSansMaison` | `int` | ✓ |  |
| `DeducMaison` | `int` | ✓ |  |
| `LiquideSeul` | `int` | ✓ |  |
| `LiquideFamille` | `int` | ✓ |  |
| `ActifMulti` | `real` | ✓ |  |
| `DateDebut` | `smalldatetime` | ✓ |  |
| `DateFin` | `smalldatetime` | ✓ |  |
| `Rowid` | `uniqueidentifier` | ✗ |  |

### `BaremeVoletEloignee`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `NoCateg` | `int` | ✓ |  |
| `DateDebut` | `smalldatetime` | ✓ |  |
| `DateFin` | `smalldatetime` | ✓ |  |
| `Seuil` | `int` | ✓ |  |
| `Volet0` | `int` | ✓ |  |
| `Volet100` | `int` | ✓ |  |
| `Volet200` | `int` | ✓ |  |
| `Volet300` | `int` | ✓ |  |
| `Volet400` | `int` | ✓ |  |
| `Volet500` | `int` | ✓ |  |
| `Volet600` | `int` | ✓ |  |
| `Volet700` | `int` | ✓ |  |
| `Volet800` | `int` | ✓ |  |
| `RowId` | `uniqueidentifier` | ✗ |  |

### `bureaux`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✗ |  |
| `region` | `char(2)` | ✗ |  |
| `coderegbur` | `char(4)` | ✗ |  |
| `bureau` | `char(35)` | ✗ |  |
| `rue` | `char(40)` | ✗ |  |
| `ville` | `char(40)` | ✗ |  |
| `province` | `char(25)` | ✗ |  |
| `codepostal` | `char(7)` | ✗ |  |
| `tel` | `char(14)` | ✗ |  |
| `fax` | `char(14)` | ✗ |  |
| `adremail` | `char(50)` | ✓ |  |
| `confweb` | `char(1)` | ✓ |  |
| `actif` | `bit` | ✓ |  |
| `dateinactif` | `date` | ✓ |  |

### `bureaux_2025`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✗ |  |
| `region` | `char(2)` | ✗ |  |
| `coderegbur` | `char(4)` | ✗ |  |
| `bureau` | `char(35)` | ✗ |  |
| `rue` | `char(40)` | ✗ |  |
| `ville` | `char(40)` | ✗ |  |
| `province` | `char(25)` | ✗ |  |
| `codepostal` | `char(7)` | ✗ |  |
| `tel` | `char(14)` | ✗ |  |
| `fax` | `char(14)` | ✗ |  |
| `adremail` | `char(50)` | ✓ |  |
| `confweb` | `char(1)` | ✓ |  |
| `actif` | `bit` | ✓ |  |
| `dateinactif` | `date` | ✓ |  |

### `BureauxMega`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✗ |  |
| `region` | `char(2)` | ✗ |  |
| `coderegbur` | `char(4)` | ✗ |  |
| `bureau` | `char(35)` | ✗ |  |
| `rue` | `char(40)` | ✗ |  |
| `ville` | `char(40)` | ✗ |  |
| `province` | `char(25)` | ✗ |  |
| `codepostal` | `char(7)` | ✗ |  |
| `tel` | `char(14)` | ✗ |  |
| `fax` | `char(14)` | ✗ |  |
| `adremail` | `char(50)` | ✓ |  |
| `confweb` | `char(1)` | ✓ |  |

### `catcivil`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(1)` | ✗ |  |
| `description` | `char(10)` | ✗ |  |

### `catdeb`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(3)` | ✗ |  |
| `description` | `char(50)` | ✗ |  |

### `cathon`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(1)` | ✗ |  |
| `description` | `char(25)` | ✗ |  |

### `catreq`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✓ |  |
| `description` | `char(32)` | ✓ |  |

### `catver`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `categorie` | `char(1)` | ✗ |  |
| `version` | `char(3)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✗ |  |

### `ConfigVals`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `iConfigID` | `int` | ✗ |  |
| `cCategory` | `varchar(20)` | ✓ |  |
| `cGroupCode` | `varchar(40)` | ✓ |  |
| `cValue` | `varchar(255)` | ✓ |  |
| `cLinkVal` | `varchar(150)` | ✓ |  |

### `convbatch`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✗ |  |
| `nom` | `varchar(25)` | ✗ |  |
| `description` | `varchar(50)` | ✗ |  |
| `manuel` | `char(1)` | ✓ |  |
| `ConvbatchID` | `int` | ✓ |  |

### `cour`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✗ |  |
| `description` | `char(50)` | ✗ |  |

### `criminel`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(5)` | ✗ |  |
| `description` | `char(60)` | ✗ |  |
| `descang` | `char(90)` | ✗ |  |
| `codenature` | `char(5)` | ✗ |  |

### `debourse`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(4)` | ✗ |  |
| `mnemonique` | `char(3)` | ✗ |  |
| `description` | `char(50)` | ✗ |  |
| `categoriecivile` | `char(1)` | ✗ |  |
| `categorie` | `char(2)` | ✗ |  |
| `nocompte` | `char(4)` | ✗ |  |

### `defdoss`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `addflig1` | `char(3)` | ✓ |  |
| `addflig2` | `char(3)` | ✓ |  |
| `addflig3` | `char(3)` | ✓ |  |
| `addflig4` | `char(3)` | ✓ |  |
| `addflig5` | `char(3)` | ✓ |  |
| `addflig6` | `char(3)` | ✓ |  |
| `addflig7` | `char(3)` | ✓ |  |
| `addflig8` | `char(3)` | ✓ |  |
| `addflig9` | `char(3)` | ✓ |  |
| `addflig10` | `char(3)` | ✓ |  |
| `addflig11` | `char(3)` | ✓ |  |
| `addflig12` | `char(3)` | ✓ |  |
| `addfpos1` | `char(2)` | ✓ |  |
| `addfpos2` | `char(2)` | ✓ |  |
| `addfpos3` | `char(2)` | ✓ |  |
| `addfpos4` | `char(2)` | ✓ |  |
| `addfpos5` | `char(2)` | ✓ |  |
| `addfpos6` | `char(2)` | ✓ |  |
| `addfpos7` | `char(2)` | ✓ |  |
| `addfpos8` | `char(2)` | ✓ |  |
| `addfpos9` | `char(2)` | ✓ |  |
| `addfpos10` | `char(2)` | ✓ |  |
| `addfpos11` | `char(2)` | ✓ |  |
| `addfpos12` | `char(2)` | ✓ |  |
| `addflng1` | `char(12)` | ✓ |  |
| `addflng2` | `char(12)` | ✓ |  |
| `addflng3` | `char(12)` | ✓ |  |
| `addflng4` | `char(12)` | ✓ |  |
| `addflng5` | `char(12)` | ✓ |  |
| `addflng6` | `char(12)` | ✓ |  |
| `addflng7` | `char(12)` | ✓ |  |
| `addflng8` | `char(12)` | ✓ |  |
| `addflng9` | `char(12)` | ✓ |  |
| `addflng10` | `char(12)` | ✓ |  |
| `addflng11` | `char(12)` | ✓ |  |
| `addflng12` | `char(12)` | ✓ |  |
| `addflngt` | `char(2)` | ✓ |  |

### `detentio`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `description` | `char(40)` | ✓ |  |

### `distance`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `ville1` | `char(50)` | ✗ |  |
| `cheflieu1` | `char(40)` | ✗ |  |
| `ville2` | `char(50)` | ✗ |  |
| `cheflieu2` | `char(40)` | ✗ |  |
| `nbkm` | `decimal(7, 2)` | ✗ |  |
| `DistanceID` | `int` | ✓ | 🔑 |

### `distance_avecdoublonc`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `ville1` | `char(50)` | ✗ |  |
| `cheflieu1` | `char(40)` | ✗ |  |
| `ville2` | `char(50)` | ✗ |  |
| `cheflieu2` | `char(40)` | ✗ |  |
| `nbkm` | `decimal(7, 2)` | ✗ |  |

### `district`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nodist` | `int` | ✗ |  |
| `nomdist` | `char(20)` | ✗ |  |
| `nomchli` | `char(30)` | ✗ |  |
| `nomsect` | `varchar(50)` | ✗ |  |
| `region` | `int` | ✓ |  |

### `etape`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✓ |  |
| `description` | `char(40)` | ✓ |  |

### `experts`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `varchar(6)` | ✗ |  |
| `nomexpert` | `varchar(50)` | ✗ |  |
| `firme` | `varchar(50)` | ✗ |  |
| `categorie` | `char(4)` | ✗ |  |
| `datemodif` | `smalldatetime` | ✓ |  |
| `adresse` | `varchar(100)` | ✓ |  |
| `ville` | `varchar(50)` | ✓ |  |
| `province` | `char(2)` | ✓ |  |
| `codepostal` | `char(7)` | ✓ |  |
| `telephone` | `char(14)` | ✓ |  |

### `experts_20251015`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(6)` | ✗ |  |
| `nomexpert` | `varchar(50)` | ✗ |  |
| `firme` | `varchar(50)` | ✗ |  |
| `categorie` | `char(4)` | ✗ |  |
| `datemodif` | `smalldatetime` | ✓ |  |
| `adresse` | `varchar(100)` | ✓ |  |
| `ville` | `varchar(50)` | ✓ |  |
| `province` | `char(2)` | ✓ |  |
| `codepostal` | `char(7)` | ✓ |  |
| `telephone` | `char(14)` | ✓ |  |

### `FermEta`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `Code` | `int` | ✗ |  |
| `Description` | `varchar(100)` | ✗ |  |
| `abrege` | `varchar(10)` | ✓ |  |
| `TypeFerme` | `char(10)` | ✓ |  |

### `forfait`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `char(6)` | ✗ |  |
| `description` | `char(30)` | ✗ |  |

### `FviPmj`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `iUpdateID` | `int` | ✓ |  |
| `cDatabase` | `varchar(20)` | ✓ |  |
| `cTable` | `varchar(20)` | ✓ |  |
| `cCle` | `varchar(255)` | ✓ |  |
| `cAction` | `char(1)` | ✓ |  |
| `dModif` | `smalldatetime` | ✓ |  |

### `greffes`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(3)` | ✗ |  |
| `description` | `char(50)` | ✗ |  |

### `groupe`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `groupe` | `char(15)` | ✗ |  |

### `IniDaj`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `ID` | `int` | ✓ |  |
| `Region` | `char(2)` | ✓ |  |
| `NoBureau` | `char(2)` | ✓ |  |
| `Ville` | `varchar(50)` | ✓ |  |
| `Appartenance` | `varchar(50)` | ✓ |  |
| `TelCodeReg` | `char(3)` | ✓ |  |
| `Static_Local` | `smallint` | ✓ |  |
| `Serveur_Central` | `varchar(50)` | ✓ |  |
| `Serveur_Maj` | `varchar(50)` | ✓ |  |
| `ADDA` | `smallint` | ✓ |  |

### `IniHomolog`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `NoBureau` | `char(2)` | ✓ |  |
| `Region` | `char(2)` | ✓ |  |
| `Ville` | `varchar(50)` | ✓ |  |
| `Appartenance` | `varchar(50)` | ✓ |  |
| `TelCodeReg` | `char(3)` | ✓ |  |
| `Static_Local` | `smallint` | ✓ |  |
| `Serveur_Central` | `varchar(50)` | ✓ |  |
| `Serveur_Maj` | `varchar(50)` | ✓ |  |
| `Email` | `nvarchar(250)` | ✓ |  |
| `Actif` | `bit` | ✓ |  |

### `interet`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `datedeb` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✗ |  |
| `pourcentage` | `float` | ✗ |  |

### `jurid`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✗ |  |
| `description` | `char(60)` | ✗ |  |

### `lienpadv`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `description` | `char(25)` | ✓ |  |
| `descang` | `char(25)` | ✓ |  |

### `liens`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `description` | `char(25)` | ✓ |  |
| `descang` | `char(25)` | ✓ |  |

### `LogModif`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `cNomTable` | `char(10)` | ✗ |  |
| `cAction` | `char(10)` | ✗ |  |
| `cUtilisateur` | `char(10)` | ✗ |  |
| `dModif` | `datetime` | ✗ |  |
| `cDateDebO` | `char(10)` | ✗ |  |
| `cDateDebC` | `char(10)` | ✗ |  |
| `cDateFinO` | `char(10)` | ✗ |  |
| `cDateFinC` | `char(10)` | ✗ |  |
| `nTarifO` | `decimal(7, 3)` | ✗ |  |
| `nTarifC` | `decimal(7, 3)` | ✗ |  |
| `cUsername` | `char(20)` | ✓ |  |
| `cProfilO` | `char(15)` | ✓ |  |
| `cProfilC` | `char(15)` | ✓ |  |

### `loi`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `Code` | `int` | ✓ |  |
| `Description` | `char(50)` | ✗ |  |

### `megaproces`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(25)` | ✓ |  |
| `description` | `varchar(100)` | ✗ |  |
| `juge` | `varchar(25)` | ✗ |  |
| `cause` | `char(17)` | ✓ |  |
| `facture` | `char(2)` | ✗ |  |
| `gouv` | `char(2)` | ✓ |  |
| `chap3` | `char(1)` | ✗ |  |

### `memoire`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(4)` | ✗ |  |
| `nom` | `varchar(50)` | ✗ |  |
| `datemodif` | `datetime` | ✓ |  |

### `mnemoexp`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(15)` | ✗ |  |
| `description` | `char(150)` | ✗ |  |

### `natcateg`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✓ |  |
| `description` | `char(40)` | ✓ |  |
| `descang` | `char(40)` | ✓ |  |

### `natgr001`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✓ |  |
| `description` | `char(25)` | ✓ |  |

### `natgr002`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✓ |  |
| `description` | `char(25)` | ✓ |  |
| `descFVI` | `varchar(25)` | ✓ |  |
| `descang` | `char(25)` | ✓ |  |

### `noligne`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(3)` | ✓ |  |

### `PalaisJustice`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `PalaisJusticeID` | `int` | ✓ |  |
| `Palais_et_points_de_service` | `varchar(500)` | ✗ |  |
| `NoPalais` | `int` | ✗ |  |
| `Districts_judiciaires` | `varchar(500)` | ✗ |  |

### `parametr`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `region` | `char(40)` | ✗ |  |
| `bureau` | `char(40)` | ✗ |  |
| `datedu` | `char(25)` | ✗ |  |
| `dateau` | `char(25)` | ✗ |  |
| `note` | `char(40)` | ✗ |  |
| `titrerapp` | `char(40)` | ✗ |  |
| `volet` | `char(40)` | ✗ |  |
| `champ` | `char(30)` | ✗ |  |

### `periodecomptable`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `periode` | `char(7)` | ✗ |  |
| `description` | `varchar(20)` | ✗ |  |

### `priorite`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `DatePriorite` | `smalldatetime` | ✓ |  |
| `Username` | `varchar(50)` | ✗ |  |

### `profilu`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nomposte` | `char(20)` | ✓ |  |
| `usern` | `char(20)` | ✗ |  |
| `nom` | `char(30)` | ✗ |  |
| `groupe` | `char(15)` | ✗ |  |
| `motpasse` | `char(9)` | ✗ |  |
| `nomaccpac` | `char(30)` | ✓ |  |
| `motpasseaccpac` | `char(10)` | ✓ |  |
| `postetel` | `char(4)` | ✓ |  |
| `suivi` | `char(3)` | ✗ |  |
| `permission` | `varchar(50)` | ✗ |  |
| `actif` | `char(1)` | ✗ |  |
| `adremail` | `varchar(50)` | ✗ |  |
| `noid` | `int` | ✗ |  |
| `rowid` | `int` | ✓ | 🔑 |

### `profilu-20260119`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nomposte` | `char(20)` | ✓ |  |
| `usern` | `char(20)` | ✗ |  |
| `nom` | `char(30)` | ✗ |  |
| `groupe` | `char(15)` | ✗ |  |
| `motpasse` | `char(9)` | ✗ |  |
| `nomaccpac` | `char(30)` | ✓ |  |
| `motpasseaccpac` | `char(10)` | ✓ |  |
| `postetel` | `char(4)` | ✓ |  |
| `suivi` | `char(3)` | ✗ |  |
| `permission` | `char(25)` | ✗ |  |
| `actif` | `char(1)` | ✗ |  |
| `adremail` | `varchar(50)` | ✗ |  |
| `noid` | `int` | ✗ |  |
| `rowid` | `int` | ✗ |  |

### `province`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(3)` | ✓ |  |
| `description` | `char(25)` | ✓ |  |
| `codeang` | `char(4)` | ✓ |  |
| `descang` | `char(25)` | ✓ |  |

### `question`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nochamp` | `char(8)` | ✓ |  |
| `question` | `char(46)` | ✓ |  |
| `referltd` | `char(1)` | ✓ |  |
| `refertable` | `char(10)` | ✓ |  |
| `defaut` | `char(10)` | ✓ |  |
| `condchet_0` | `char(10)` | ✓ |  |
| `condchopet` | `char(10)` | ✓ |  |
| `condchcrit` | `char(20)` | ✓ |  |
| `condchet_1` | `char(10)` | ✓ |  |
| `condchope2` | `char(10)` | ✓ |  |
| `condchcri2` | `char(20)` | ✓ |  |
| `condchet_2` | `char(10)` | ✓ |  |
| `condchope3` | `char(10)` | ✓ |  |
| `condchcri3` | `char(20)` | ✓ |  |
| `condchou_0` | `char(10)` | ✓ |  |
| `condchopou` | `char(10)` | ✓ |  |
| `condchcri4` | `char(20)` | ✓ |  |
| `condchou_1` | `char(10)` | ✓ |  |
| `condchopo2` | `char(10)` | ✓ |  |
| `condchcri5` | `char(20)` | ✓ |  |
| `condchou_2` | `char(10)` | ✓ |  |
| `condchopo3` | `char(10)` | ✓ |  |
| `condchcri6` | `char(20)` | ✓ |  |
| `sicondchvr` | `char(10)` | ✓ |  |
| `sicondchfa` | `char(10)` | ✓ |  |
| `condafet_0` | `char(10)` | ✓ |  |
| `condafopet` | `char(10)` | ✓ |  |
| `condafcrit` | `char(20)` | ✓ |  |
| `condafet_1` | `char(10)` | ✓ |  |
| `condafope2` | `char(10)` | ✓ |  |
| `condafcri2` | `char(20)` | ✓ |  |
| `condafet_2` | `char(10)` | ✓ |  |
| `condafope3` | `char(10)` | ✓ |  |
| `condafcri3` | `char(20)` | ✓ |  |
| `condafou_0` | `char(10)` | ✓ |  |
| `condafopou` | `char(10)` | ✓ |  |
| `condafcri4` | `char(20)` | ✓ |  |
| `condafou_1` | `char(10)` | ✓ |  |
| `condafopo2` | `char(10)` | ✓ |  |
| `condafcri5` | `char(20)` | ✓ |  |
| `condafou_2` | `char(10)` | ✓ |  |
| `condafopo3` | `char(10)` | ✓ |  |
| `condafcri6` | `char(20)` | ✓ |  |
| `sicondafvr` | `char(10)` | ✓ |  |
| `sicondaffa` | `char(10)` | ✓ |  |
| `aide` | `char(254)` | ✓ |  |
| `validsiet_` | `char(10)` | ✓ |  |
| `validsiope` | `char(10)` | ✓ |  |
| `validsicri` | `char(20)` | ✓ |  |
| `validsiet2` | `char(10)` | ✓ |  |
| `validsiop2` | `char(10)` | ✓ |  |
| `validsicr2` | `char(20)` | ✓ |  |
| `validsiet3` | `char(10)` | ✓ |  |
| `validsiop3` | `char(10)` | ✓ |  |
| `validsicr3` | `char(20)` | ✓ |  |
| `validsiou_` | `char(10)` | ✓ |  |
| `validsiopo` | `char(10)` | ✓ |  |
| `validsicr4` | `char(20)` | ✓ |  |
| `validsiou2` | `char(10)` | ✓ |  |
| `validsiop4` | `char(10)` | ✓ |  |
| `validsicr5` | `char(20)` | ✓ |  |
| `validsiou3` | `char(10)` | ✓ |  |
| `validsiop5` | `char(10)` | ✓ |  |
| `validsicr6` | `char(20)` | ✓ |  |
| `validsialo` | `char(200)` | ✓ |  |
| `validcrois` | `char(10)` | ✓ |  |
| `validdescr` | `char(100)` | ✓ |  |

### `raisNt`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `varchar(5)` | ✗ |  |
| `description` | `varchar(150)` | ✗ |  |
| `mnemonique` | `char(2)` | ✗ |  |
| `textefacture` | `varchar(1000)` | ✓ |  |

### `raisoann`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✗ |  |
| `description` | `char(25)` | ✗ |  |

### `raisorev`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(1)` | ✗ |  |
| `description` | `char(20)` | ✗ |  |
| `priorite` | `int` | ✓ |  |

### `rappel`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(15)` | ✓ |  |
| `description` | `char(25)` | ✓ |  |

### `rapport`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `titre` | `char(13)` | ✓ |  |
| `description` | `varchar(100)` | ✓ |  |
| `nommenu` | `varchar(15)` | ✓ |  |
| `site` | `char(1)` | ✓ |  |
| `RapportTypeID` | `int` | ✓ |  |
| `Actif` | `bit` | ✓ |  |
| `RapportID` | `int` | ✗ |  |
| `fRegion` | `bit` | ✓ |  |
| `fBureau` | `bit` | ✓ |  |
| `fDate` | `bit` | ✓ |  |
| `fStatut` | `bit` | ✓ |  |
| `fCheminement` | `bit` | ✓ |  |
| `fCategorie` | `bit` | ✓ |  |
| `fService` | `bit` | ✓ |  |
| `fProfType` | `bit` | ✓ |  |
| `fAvocat` | `bit` | ✓ |  |
| `fVCVG` | `bit` | ✓ |  |
| `pUsrRpt` | `bit` | ✓ |  |
| `CopyRpt` | `bit` | ✓ |  |
| `DateLastUpd` | `smalldatetime` | ✓ |  |

### `Rapports52`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `sNomRap` | `varchar(50)` | ✗ |  |
| `sDescRap` | `varchar(100)` | ✗ |  |
| `sGroupRap` | `varchar(20)` | ✗ |  |
| `sPermRap` | `varchar(100)` | ✗ |  |
| `iOrder` | `int` | ✗ |  |

### `revperio`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(1)` | ✓ |  |
| `description` | `varchar(31)` | ✓ |  |
| `facteur` | `decimal(7, 5)` | ✓ |  |

### `revsourc`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `noligne` | `char(3)` | ✓ |  |
| `description` | `char(25)` | ✓ |  |
| `descang` | `char(25)` | ✓ |  |

### `statfac`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(1)` | ✗ |  |
| `description` | `char(15)` | ✗ |  |
| `descFVI` | `varchar(15)` | ✓ |  |
| `revisable` | `int` | ✗ |  |
| `statut` | `int` | ✓ |  |

### `statuts`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(1)` | ✓ |  |
| `description` | `char(15)` | ✓ |  |

### `tarifskm`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✗ |  |
| `prixkm` | `decimal(7, 3)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✓ |  |

### `taxes`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(2)` | ✗ |  |
| `nomtaxe` | `char(5)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✗ |  |
| `pourcentage` | `decimal(5, 3)` | ✗ |  |

### `tbVerifMaj`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `idSql` | `uniqueidentifier` | ✗ |  |
| `strSelect` | `nvarchar(500)` | ✓ |  |
| `strFrom` | `nvarchar(200)` | ✓ |  |
| `strWhere` | `nvarchar(200)` | ✓ |  |
| `strOrderBy` | `nvarchar(200)` | ✓ |  |
| `strNom` | `nvarchar(200)` | ✓ |  |
| `strBD` | `nvarchar(100)` | ✓ |  |
| `strTable` | `nvarchar(50)` | ✓ |  |

### `tJourFeriee`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `JourFerieeID` | `int` | ✗ |  |
| `JourDate` | `date` | ✓ |  |
| `DsJourFeriee` | `varchar(250)` | ✓ |  |

### `tJourType`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `JourTypeID` | `int` | ✓ |  |
| `DsJourType` | `varchar(250)` | ✓ |  |
| `Abreviation` | `varchar(50)` | ✓ |  |
| `HrsHoraire` | `bit` | ✓ |  |
| `HrsTravailler` | `int` | ✓ |  |
| `MinTravailler` | `int` | ✓ |  |
| `ModifierHrs` | `bit` | ✓ |  |
| `TempsTrav` | `bit` | ✓ |  |
| `TempsDebit` | `bit` | ✓ |  |
| `TempsDebitUtil` | `bit` | ✓ |  |
| `TypeFuture` | `bit` | ✓ |  |
| `ApprovLot` | `bit` | ✓ |  |
| `CommObl` | `bit` | ✓ |  |
| `Actif` | `bit` | ✓ |  |
| `UsagerIDC` | `int` | ✓ |  |
| `DateC` | `datetime` | ✓ |  |
| `UsagerIDM` | `int` | ✓ |  |
| `DateM` | `datetime` | ✓ |  |

### `tPonderationFermNatgr`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `CodeFermeEta` | `int` | ✓ |  |
| `Natgr2Code` | `char(2)` | ✗ |  |
| `Ponderation` | `numeric(4, 2)` | ✓ |  |
| `DateC` | `smalldatetime` | ✓ |  |

### `tProfType`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `ProfTypeID` | `char(1)` | ✗ |  |
| `DsProfType` | `varchar(150)` | ✓ |  |
| `Actif` | `bit` | ✓ |  |

### `tRapportType`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `RapportTypeID` | `int` | ✗ |  |
| `DsRapportType` | `varchar(250)` | ✓ |  |
| `Actif` | `bit` | ✓ |  |

### `typtrait`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `type` | `char(11)` | ✓ |  |

---

## 📦 Base `sArt52`

**126 tables détectées.**

### `factureRetro`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `pcdb200` | `varchar(40)` | ✓ |  |
| `pcdb202` | `varchar(60)` | ✓ |  |
| `pcdb204` | `varchar(60)` | ✓ |  |
| `pcdb206` | `varchar(50)` | ✓ |  |
| `pcdb220` | `varchar(80)` | ✓ |  |
| `pcdb222` | `varchar(60)` | ✓ |  |
| `pcdb224` | `varchar(60)` | ✓ |  |
| `pcdb226` | `varchar(40)` | ✓ |  |
| `noref` | `char(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pcdb308` | `varchar(30)` | ✓ |  |
| `pcdbnocause` | `varchar(17)` | ✓ |  |
| `pcdb380` | `varchar(80)` | ✓ |  |
| `pcdb382` | `smalldatetime` | ✓ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdb386` | `smalldatetime` | ✓ |  |
| `pcdbcodenat` | `varchar(6)` | ✓ |  |
| `pcdbnoch` | `varchar(20)` | ✓ |  |
| `pcdbdatech` | `smalldatetime` | ✓ |  |
| `pcdbtotal` | `decimal(15, 2)` | ✓ |  |
| `pcdbidapp` | `varchar(10)` | ✓ |  |
| `pcdbidsai` | `varchar(10)` | ✓ |  |
| `pcdbdatesai` | `smalldatetime` | ✓ |  |
| `pcdbdateapp` | `smalldatetime` | ✓ |  |
| `pcdbdateappspec` | `smalldatetime` | ✓ |  |
| `pcdbdateprpmnt` | `smalldatetime` | ✓ |  |
| `pcdbstatut` | `char(1)` | ✓ |  |
| `pcdbcoderairev` | `char(1)` | ✓ |  |
| `pcdbdateccj` | `smalldatetime` | ✓ |  |
| `pcdbdatefac` | `smalldatetime` | ✓ |  |
| `pcdbdatecsj` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `pcdbmontant` | `decimal(15, 2)` | ✓ |  |
| `pcdbmontantrecl` | `decimal(15, 2)` | ✓ |  |
| `pcdbavopay` | `char(1)` | ✓ |  |
| `pcdbtxtavis` | `varchar(5000)` | ✓ |  |
| `pcdbfacferme` | `char(1)` | ✓ |  |
| `pcdbfacpaye` | `char(2)` | ✓ |  |
| `pcdbmontcontrib` | `decimal(15, 2)` | ✓ |  |
| `pcdbvoletcontrib` | `char(1)` | ✓ |  |
| `pcdbraisannul` | `char(2)` | ✓ |  |
| `pcdbdateannul` | `smalldatetime` | ✓ |  |
| `pcdbinterets` | `decimal(15, 2)` | ✓ |  |
| `pcdblotfact` | `varchar(10)` | ✓ |  |
| `pcdblotpaie` | `varchar(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcdbart87` | `char(1)` | ✓ |  |
| `pcdbouvert` | `int` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ | 🔑 |
| `pcdbcontcalc` | `decimal(8, 2)` | ✓ |  |
| `pcdbnote` | `varchar(5000)` | ✓ |  |
| `pcdbadverse` | `varchar(50)` | ✓ |  |
| `pcdbcour` | `varchar(50)` | ✓ |  |
| `pcdbdistrict` | `varchar(25)` | ✓ |  |
| `pcdbnomloi` | `varchar(255)` | ✓ |  |
| `pcdbarticle` | `varchar(25)` | ✓ |  |
| `pcdbcomavo` | `varchar(7050)` | ✓ |  |
| `pcdbcomccj` | `varchar(5000)` | ✓ |  |
| `pcdbpj` | `char(1)` | ✓ |  |
| `pcdbinterim` | `char(1)` | ✓ |  |
| `nodossier` | `varchar(17)` | ✗ |  |
| `periodecompt` | `char(7)` | ✗ |  |
| `pcdbfirme` | `varchar(150)` | ✓ |  |
| `pcdbnoTPS` | `varchar(25)` | ✓ |  |
| `pcdbnoTVQ` | `varchar(25)` | ✓ |  |
| `pcdbmtTPS` | `decimal(18, 2)` | ✓ |  |
| `pcdbmtTVQ` | `decimal(18, 2)` | ✓ |  |
| `OkDelete` | `bit` | ✓ |  |
| `pcdbnoteRemb` | `varchar(5000)` | ✓ |  |
| `pcdbauteurNRemb` | `varchar(200)` | ✓ |  |
| `nofactrevSource` | `varchar(16)` | ✓ |  |
| `ConvBatchID` | `int` | ✓ |  |
| `Traitee` | `bit` | ✓ |  |
| `DateTraitee` | `datetime` | ✓ |  |
| `NT` | `bit` | ✗ |  |

### `honorairRetro`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pchodateserv` | `smalldatetime` | ✓ |  |
| `pchonotarif` | `varchar(20)` | ✗ |  |
| `pchoverstarif` | `char(3)` | ✗ |  |
| `pchocattarif` | `char(1)` | ✗ |  |
| `pchomontreclame` | `decimal(15, 2)` | ✗ |  |
| `pchomontpaye` | `decimal(15, 2)` | ✗ |  |
| `pchocomm` | `varchar(100)` | ✓ |  |
| `pchostatut` | `char(1)` | ✓ |  |
| `pchodatestatut` | `smalldatetime` | ✓ |  |
| `pchoapp` | `int` | ✓ |  |
| `pchodateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pchonoseq` | `int` | ✓ |  |
| `pchoraisnt` | `char(1)` | ✗ |  |
| `HonorairID` | `int` | ✓ | 🔑 |

### `facture`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `pcdb200` | `varchar(40)` | ✓ |  |
| `pcdb202` | `varchar(60)` | ✓ |  |
| `pcdb204` | `varchar(60)` | ✓ |  |
| `pcdb206` | `varchar(50)` | ✓ |  |
| `pcdb220` | `varchar(80)` | ✓ |  |
| `pcdb222` | `varchar(60)` | ✓ |  |
| `pcdb224` | `varchar(60)` | ✓ |  |
| `pcdb226` | `varchar(40)` | ✓ |  |
| `noref` | `char(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pcdb308` | `varchar(30)` | ✓ |  |
| `pcdbnocause` | `varchar(17)` | ✓ |  |
| `pcdb380` | `varchar(80)` | ✓ |  |
| `pcdb382` | `smalldatetime` | ✓ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdb386` | `smalldatetime` | ✓ |  |
| `pcdbcodenat` | `varchar(6)` | ✓ |  |
| `pcdbnoch` | `varchar(20)` | ✓ |  |
| `pcdbdatech` | `smalldatetime` | ✓ |  |
| `pcdbtotal` | `decimal(15, 2)` | ✓ |  |
| `pcdbidapp` | `varchar(10)` | ✓ |  |
| `pcdbidsai` | `varchar(10)` | ✓ |  |
| `pcdbdatesai` | `smalldatetime` | ✓ |  |
| `pcdbdateapp` | `smalldatetime` | ✓ |  |
| `pcdbdateappspec` | `smalldatetime` | ✓ |  |
| `pcdbdateprpmnt` | `smalldatetime` | ✓ |  |
| `pcdbstatut` | `char(1)` | ✓ |  |
| `pcdbcoderairev` | `char(1)` | ✓ |  |
| `pcdbdateccj` | `smalldatetime` | ✓ |  |
| `pcdbdatefac` | `smalldatetime` | ✓ |  |
| `pcdbdatecsj` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `pcdbmontant` | `decimal(15, 2)` | ✓ |  |
| `pcdbmontantrecl` | `decimal(15, 2)` | ✓ |  |
| `pcdbavopay` | `char(1)` | ✓ |  |
| `pcdbtxtavis` | `varchar(5000)` | ✓ |  |
| `pcdbfacferme` | `char(1)` | ✓ |  |
| `pcdbfacpaye` | `char(2)` | ✓ |  |
| `pcdbmontcontrib` | `decimal(15, 2)` | ✓ |  |
| `pcdbvoletcontrib` | `char(1)` | ✓ |  |
| `pcdbraisannul` | `char(2)` | ✓ |  |
| `pcdbdateannul` | `smalldatetime` | ✓ |  |
| `pcdbinterets` | `decimal(15, 2)` | ✓ |  |
| `pcdblotfact` | `varchar(10)` | ✓ |  |
| `pcdblotpaie` | `varchar(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcdbart87` | `char(1)` | ✓ |  |
| `pcdbouvert` | `int` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdbcontcalc` | `decimal(8, 2)` | ✓ |  |
| `pcdbnote` | `varchar(5000)` | ✓ |  |
| `pcdbadverse` | `varchar(50)` | ✓ |  |
| `pcdbcour` | `varchar(50)` | ✓ |  |
| `pcdbdistrict` | `varchar(25)` | ✓ |  |
| `pcdbnomloi` | `varchar(255)` | ✓ |  |
| `pcdbarticle` | `varchar(25)` | ✓ |  |
| `pcdbcomavo` | `varchar(7050)` | ✓ |  |
| `pcdbcomccj` | `varchar(5000)` | ✓ |  |
| `pcdbpj` | `char(1)` | ✓ |  |
| `pcdbinterim` | `char(1)` | ✓ |  |
| `nodossier` | `varchar(17)` | ✗ |  |
| `periodecompt` | `char(7)` | ✗ |  |
| `pcdbfirme` | `varchar(150)` | ✓ |  |
| `pcdbnoTPS` | `varchar(25)` | ✓ |  |
| `pcdbnoTVQ` | `varchar(25)` | ✓ |  |
| `pcdbmtTPS` | `decimal(18, 2)` | ✓ |  |
| `pcdbmtTVQ` | `decimal(18, 2)` | ✓ |  |
| `OkDelete` | `bit` | ✓ |  |
| `pcdbnoteRemb` | `varchar(5000)` | ✓ |  |
| `pcdbauteurNRemb` | `varchar(200)` | ✓ |  |

### `debourse`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(12)` | ✓ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pcdecodedeb` | `char(4)` | ✗ |  |
| `pcdedatedeb` | `smalldatetime` | ✗ |  |
| `pcdemontreclame` | `decimal(15, 2)` | ✗ |  |
| `pcdemontpaye` | `decimal(15, 2)` | ✗ |  |
| `pcdecomm` | `varchar(100)` | ✓ |  |
| `pcdestatut` | `char(1)` | ✓ |  |
| `pcdedatestatut` | `smalldatetime` | ✓ |  |
| `pcdeapp` | `int` | ✓ |  |
| `pcdedateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdenoseq` | `int` | ✓ |  |
| `pcdeexpert` | `varchar(6)` | ✓ |  |

### `Thonorsta2020`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✗ |  |
| `tarif` | `decimal(15, 2)` | ✗ |  |
| `Ntarif` | `decimal(15, 2)` | ✗ |  |

### `honorsta`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✗ |  |
| `categorie` | `char(1)` | ✗ |  |
| `version` | `char(3)` | ✗ |  |
| `description` | `varchar(50)` | ✗ |  |
| `tarif` | `decimal(15, 2)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✓ |  |
| `forfait` | `char(1)` | ✓ |  |
| `mnemoforfait` | `varchar(10)` | ✓ |  |
| `equivalence` | `varchar(15)` | ✓ |  |
| `convbatchID` | `int` | ✓ |  |

### `honorair`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pchodateserv` | `smalldatetime` | ✓ |  |
| `pchonotarif` | `varchar(20)` | ✗ |  |
| `pchoverstarif` | `char(3)` | ✗ |  |
| `pchocattarif` | `char(1)` | ✗ |  |
| `pchomontreclame` | `decimal(15, 2)` | ✗ |  |
| `pchomontpaye` | `decimal(15, 2)` | ✗ |  |
| `pchocomm` | `varchar(100)` | ✓ |  |
| `pchostatut` | `char(1)` | ✓ |  |
| `pchodatestatut` | `smalldatetime` | ✓ |  |
| `pchoapp` | `int` | ✓ |  |
| `pchodateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pchonoseq` | `int` | ✓ |  |
| `pchoraisnt` | `char(1)` | ✗ |  |

### `extraction`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `no_facture` | `varchar(13)` | ✗ |  |
| `no_revision` | `int` | ✗ |  |
| `nom_avoc` | `varchar(40)` | ✓ |  |
| `nom_client` | `varchar(80)` | ✓ |  |
| `no_ref` | `varchar(11)` | ✓ |  |
| `no_region` | `varchar(2)` | ✗ |  |
| `no_bureau` | `varchar(2)` | ✗ |  |
| `no_seq_daj` | `varchar(12)` | ✓ |  |
| `no_cause` | `varchar(17)` | ✓ |  |
| `date_mandat` | `smalldatetime` | ✗ |  |
| `date_effec` | `smalldatetime` | ✓ |  |
| `code_nature` | `varchar(6)` | ✓ |  |
| `date_cheque` | `smalldatetime` | ✓ |  |
| `no_cheque` | `varchar(20)` | ✓ |  |
| `date_ccj` | `smalldatetime` | ✓ |  |
| `date_facture` | `smalldatetime` | ✓ |  |
| `total_fac` | `decimal(15, 2)` | ✓ |  |
| `date_fisc` | `varchar(4)` | ✓ |  |
| `statut` | `varchar(1)` | ✗ |  |
| `code_raison` | `varchar(1)` | ✓ |  |
| `code_avo_mand` | `varchar(6)` | ✗ |  |
| `mont_cont` | `decimal(15, 2)` | ✓ |  |
| `volet_cont` | `varchar(1)` | ✓ |  |
| `date_annul` | `smalldatetime` | ✓ |  |
| `interet` | `decimal(15, 2)` | ✓ |  |
| `cont_calc` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `km_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `km_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `no_fact_rev` | `varchar(16)` | ✗ |  |
| `conv_batch` | `varchar(2)` | ✓ |  |
| `periodecompt` | `char(7)` | ✓ |  |
| `dh_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `avo_ass_paye` | `decimal(18, 0)` | ✓ |  |
| `tps` | `decimal(18, 2)` | ✓ |  |
| `tvq` | `decimal(18, 2)` | ✓ |  |
| `nt174` | `decimal(15, 2)` | ✓ |  |

### `recouv`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `matiere` | `varchar(100)` | ✓ |  |

### `kilometr`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pckmorigdest` | `varchar(100)` | ✗ |  |
| `pckmdatekm` | `smalldatetime` | ✗ |  |
| `pckmnbkm` | `decimal(7, 2)` | ✓ |  |
| `pckmmontreclame` | `decimal(15, 2)` | ✗ |  |
| `pckmmontpaye` | `decimal(15, 2)` | ✗ |  |
| `pckmcomm` | `varchar(100)` | ✓ |  |
| `pckmstatut` | `char(1)` | ✓ |  |
| `pckmdatestatut` | `smalldatetime` | ✓ |  |
| `pckmapp` | `int` | ✓ |  |
| `pckmdateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pckmnoseq` | `int` | ✓ |  |

### `nocauses`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pccanocause` | `varchar(17)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pccanature` | `char(6)` | ✓ |  |
| `pccadatefac` | `smalldatetime` | ✓ |  |
| `pccacodeavo` | `char(6)` | ✓ |  |
| `pccanomcli` | `varchar(80)` | ✓ |  |
| `pccastatut` | `char(2)` | ✓ |  |
| `pccaprincipale` | `char(1)` | ✓ |  |
| `pccacatregr` | `char(2)` | ✓ |  |
| `pccastatfac` | `char(1)` | ✓ |  |
| `pccaidutil` | `varchar(10)` | ✓ |  |
| `modifiepar` | `varchar(20)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |

### `tfacture_avant_2011`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `pcdb200` | `varchar(40)` | ✓ |  |
| `pcdb202` | `varchar(60)` | ✓ |  |
| `pcdb204` | `varchar(60)` | ✓ |  |
| `pcdb206` | `varchar(50)` | ✓ |  |
| `pcdb220` | `varchar(80)` | ✓ |  |
| `pcdb222` | `varchar(60)` | ✓ |  |
| `pcdb224` | `varchar(60)` | ✓ |  |
| `pcdb226` | `varchar(40)` | ✓ |  |
| `noref` | `char(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pcdb308` | `varchar(30)` | ✓ |  |
| `pcdbnocause` | `varchar(17)` | ✓ |  |
| `pcdb380` | `varchar(80)` | ✓ |  |
| `pcdb382` | `smalldatetime` | ✓ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdb386` | `smalldatetime` | ✓ |  |
| `pcdbcodenat` | `varchar(6)` | ✓ |  |
| `pcdbnoch` | `varchar(20)` | ✓ |  |
| `pcdbdatech` | `smalldatetime` | ✓ |  |
| `pcdbtotal` | `decimal(15, 2)` | ✓ |  |
| `pcdbidapp` | `varchar(10)` | ✓ |  |
| `pcdbidsai` | `varchar(10)` | ✓ |  |
| `pcdbdatesai` | `smalldatetime` | ✓ |  |
| `pcdbdateapp` | `smalldatetime` | ✓ |  |
| `pcdbdateappspec` | `smalldatetime` | ✓ |  |
| `pcdbdateprpmnt` | `smalldatetime` | ✓ |  |
| `pcdbstatut` | `char(1)` | ✓ |  |
| `pcdbcoderairev` | `char(1)` | ✓ |  |
| `pcdbdateccj` | `smalldatetime` | ✓ |  |
| `pcdbdatefac` | `smalldatetime` | ✓ |  |
| `pcdbdatecsj` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `pcdbmontant` | `decimal(15, 2)` | ✓ |  |
| `pcdbmontantrecl` | `decimal(15, 2)` | ✓ |  |
| `pcdbavopay` | `char(1)` | ✓ |  |
| `pcdbtxtavis` | `varchar(5000)` | ✓ |  |
| `pcdbfacferme` | `char(1)` | ✓ |  |
| `pcdbfacpaye` | `char(2)` | ✓ |  |
| `pcdbmontcontrib` | `decimal(15, 2)` | ✓ |  |
| `pcdbvoletcontrib` | `char(1)` | ✓ |  |
| `pcdbraisannul` | `char(2)` | ✓ |  |
| `pcdbdateannul` | `smalldatetime` | ✓ |  |
| `pcdbinterets` | `decimal(15, 2)` | ✓ |  |
| `pcdblotfact` | `varchar(10)` | ✓ |  |
| `pcdblotpaie` | `varchar(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcdbart87` | `char(1)` | ✓ |  |
| `pcdbouvert` | `int` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdbcontcalc` | `decimal(8, 2)` | ✓ |  |
| `pcdbnote` | `varchar(5000)` | ✓ |  |
| `pcdbadverse` | `varchar(50)` | ✓ |  |
| `pcdbcour` | `varchar(50)` | ✓ |  |
| `pcdbdistrict` | `varchar(25)` | ✓ |  |
| `pcdbnomloi` | `varchar(255)` | ✓ |  |
| `pcdbarticle` | `varchar(25)` | ✓ |  |
| `pcdbcomavo` | `varchar(7050)` | ✓ |  |
| `pcdbcomccj` | `varchar(5000)` | ✓ |  |
| `pcdbpj` | `char(1)` | ✓ |  |
| `pcdbinterim` | `char(1)` | ✓ |  |
| `nodossier` | `varchar(17)` | ✗ |  |
| `periodecompt` | `char(7)` | ✗ |  |
| `pcdbfirme` | `varchar(150)` | ✓ |  |
| `pcdbnoTPS` | `varchar(25)` | ✓ |  |
| `pcdbnoTVQ` | `varchar(25)` | ✓ |  |
| `pcdbmtTPS` | `decimal(18, 2)` | ✓ |  |
| `pcdbmtTVQ` | `decimal(18, 2)` | ✓ |  |
| `OkDelete` | `bit` | ✓ |  |
| `pcdbnoteRemb` | `varchar(5000)` | ✓ |  |
| `pcdbauteurNRemb` | `varchar(200)` | ✓ |  |
| `FolderNotFound` | `bit` | ✓ |  |
| `FileNotFound` | `bit` | ✓ |  |
| `Moved` | `bit` | ✓ |  |

### `tfacture_avant_2000`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `pcdb200` | `varchar(40)` | ✓ |  |
| `pcdb202` | `varchar(60)` | ✓ |  |
| `pcdb204` | `varchar(60)` | ✓ |  |
| `pcdb206` | `varchar(50)` | ✓ |  |
| `pcdb220` | `varchar(80)` | ✓ |  |
| `pcdb222` | `varchar(60)` | ✓ |  |
| `pcdb224` | `varchar(60)` | ✓ |  |
| `pcdb226` | `varchar(40)` | ✓ |  |
| `noref` | `char(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pcdb308` | `varchar(30)` | ✓ |  |
| `pcdbnocause` | `varchar(17)` | ✓ |  |
| `pcdb380` | `varchar(80)` | ✓ |  |
| `pcdb382` | `smalldatetime` | ✓ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdb386` | `smalldatetime` | ✓ |  |
| `pcdbcodenat` | `varchar(6)` | ✓ |  |
| `pcdbnoch` | `varchar(20)` | ✓ |  |
| `pcdbdatech` | `smalldatetime` | ✓ |  |
| `pcdbtotal` | `decimal(15, 2)` | ✓ |  |
| `pcdbidapp` | `varchar(10)` | ✓ |  |
| `pcdbidsai` | `varchar(10)` | ✓ |  |
| `pcdbdatesai` | `smalldatetime` | ✓ |  |
| `pcdbdateapp` | `smalldatetime` | ✓ |  |
| `pcdbdateappspec` | `smalldatetime` | ✓ |  |
| `pcdbdateprpmnt` | `smalldatetime` | ✓ |  |
| `pcdbstatut` | `char(1)` | ✓ |  |
| `pcdbcoderairev` | `char(1)` | ✓ |  |
| `pcdbdateccj` | `smalldatetime` | ✓ |  |
| `pcdbdatefac` | `smalldatetime` | ✓ |  |
| `pcdbdatecsj` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `pcdbmontant` | `decimal(15, 2)` | ✓ |  |
| `pcdbmontantrecl` | `decimal(15, 2)` | ✓ |  |
| `pcdbavopay` | `char(1)` | ✓ |  |
| `pcdbtxtavis` | `varchar(5000)` | ✓ |  |
| `pcdbfacferme` | `char(1)` | ✓ |  |
| `pcdbfacpaye` | `char(2)` | ✓ |  |
| `pcdbmontcontrib` | `decimal(15, 2)` | ✓ |  |
| `pcdbvoletcontrib` | `char(1)` | ✓ |  |
| `pcdbraisannul` | `char(2)` | ✓ |  |
| `pcdbdateannul` | `smalldatetime` | ✓ |  |
| `pcdbinterets` | `decimal(15, 2)` | ✓ |  |
| `pcdblotfact` | `varchar(10)` | ✓ |  |
| `pcdblotpaie` | `varchar(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcdbart87` | `char(1)` | ✓ |  |
| `pcdbouvert` | `int` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdbcontcalc` | `decimal(8, 2)` | ✓ |  |
| `pcdbnote` | `varchar(5000)` | ✓ |  |
| `pcdbadverse` | `varchar(50)` | ✓ |  |
| `pcdbcour` | `varchar(50)` | ✓ |  |
| `pcdbdistrict` | `varchar(25)` | ✓ |  |
| `pcdbnomloi` | `varchar(255)` | ✓ |  |
| `pcdbarticle` | `varchar(25)` | ✓ |  |
| `pcdbcomavo` | `varchar(7050)` | ✓ |  |
| `pcdbcomccj` | `varchar(5000)` | ✓ |  |
| `pcdbpj` | `char(1)` | ✓ |  |
| `pcdbinterim` | `char(1)` | ✓ |  |
| `nodossier` | `varchar(17)` | ✗ |  |
| `periodecompt` | `char(7)` | ✗ |  |
| `pcdbfirme` | `varchar(150)` | ✓ |  |
| `pcdbnoTPS` | `varchar(25)` | ✓ |  |
| `pcdbnoTVQ` | `varchar(25)` | ✓ |  |
| `pcdbmtTPS` | `decimal(18, 2)` | ✓ |  |
| `pcdbmtTVQ` | `decimal(18, 2)` | ✓ |  |
| `OkDelete` | `bit` | ✓ |  |

### `tfacture_avant_2005`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `pcdb200` | `varchar(40)` | ✓ |  |
| `pcdb202` | `varchar(60)` | ✓ |  |
| `pcdb204` | `varchar(60)` | ✓ |  |
| `pcdb206` | `varchar(50)` | ✓ |  |
| `pcdb220` | `varchar(80)` | ✓ |  |
| `pcdb222` | `varchar(60)` | ✓ |  |
| `pcdb224` | `varchar(60)` | ✓ |  |
| `pcdb226` | `varchar(40)` | ✓ |  |
| `noref` | `char(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pcdb308` | `varchar(30)` | ✓ |  |
| `pcdbnocause` | `varchar(17)` | ✓ |  |
| `pcdb380` | `varchar(80)` | ✓ |  |
| `pcdb382` | `smalldatetime` | ✓ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdb386` | `smalldatetime` | ✓ |  |
| `pcdbcodenat` | `varchar(6)` | ✓ |  |
| `pcdbnoch` | `varchar(20)` | ✓ |  |
| `pcdbdatech` | `smalldatetime` | ✓ |  |
| `pcdbtotal` | `decimal(15, 2)` | ✓ |  |
| `pcdbidapp` | `varchar(10)` | ✓ |  |
| `pcdbidsai` | `varchar(10)` | ✓ |  |
| `pcdbdatesai` | `smalldatetime` | ✓ |  |
| `pcdbdateapp` | `smalldatetime` | ✓ |  |
| `pcdbdateappspec` | `smalldatetime` | ✓ |  |
| `pcdbdateprpmnt` | `smalldatetime` | ✓ |  |
| `pcdbstatut` | `char(1)` | ✓ |  |
| `pcdbcoderairev` | `char(1)` | ✓ |  |
| `pcdbdateccj` | `smalldatetime` | ✓ |  |
| `pcdbdatefac` | `smalldatetime` | ✓ |  |
| `pcdbdatecsj` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `pcdbmontant` | `decimal(15, 2)` | ✓ |  |
| `pcdbmontantrecl` | `decimal(15, 2)` | ✓ |  |
| `pcdbavopay` | `char(1)` | ✓ |  |
| `pcdbtxtavis` | `varchar(5000)` | ✓ |  |
| `pcdbfacferme` | `char(1)` | ✓ |  |
| `pcdbfacpaye` | `char(2)` | ✓ |  |
| `pcdbmontcontrib` | `decimal(15, 2)` | ✓ |  |
| `pcdbvoletcontrib` | `char(1)` | ✓ |  |
| `pcdbraisannul` | `char(2)` | ✓ |  |
| `pcdbdateannul` | `smalldatetime` | ✓ |  |
| `pcdbinterets` | `decimal(15, 2)` | ✓ |  |
| `pcdblotfact` | `varchar(10)` | ✓ |  |
| `pcdblotpaie` | `varchar(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcdbart87` | `char(1)` | ✓ |  |
| `pcdbouvert` | `int` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdbcontcalc` | `decimal(8, 2)` | ✓ |  |
| `pcdbnote` | `varchar(5000)` | ✓ |  |
| `pcdbadverse` | `varchar(50)` | ✓ |  |
| `pcdbcour` | `varchar(50)` | ✓ |  |
| `pcdbdistrict` | `varchar(25)` | ✓ |  |
| `pcdbnomloi` | `varchar(255)` | ✓ |  |
| `pcdbarticle` | `varchar(25)` | ✓ |  |
| `pcdbcomavo` | `varchar(7050)` | ✓ |  |
| `pcdbcomccj` | `varchar(5000)` | ✓ |  |
| `pcdbpj` | `char(1)` | ✓ |  |
| `pcdbinterim` | `char(1)` | ✓ |  |
| `nodossier` | `varchar(17)` | ✗ |  |
| `periodecompt` | `char(7)` | ✗ |  |
| `pcdbfirme` | `varchar(150)` | ✓ |  |
| `pcdbnoTPS` | `varchar(25)` | ✓ |  |
| `pcdbnoTVQ` | `varchar(25)` | ✓ |  |
| `pcdbmtTPS` | `decimal(18, 2)` | ✓ |  |
| `pcdbmtTVQ` | `decimal(18, 2)` | ✓ |  |
| `OkDelete` | `bit` | ✓ |  |
| `FolderNotFound` | `bit` | ✓ |  |
| `FileNotFound` | `bit` | ✓ |  |
| `Moved` | `bit` | ✓ |  |

### `tfacture_avant_2008`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `pcdb200` | `varchar(40)` | ✓ |  |
| `pcdb202` | `varchar(60)` | ✓ |  |
| `pcdb204` | `varchar(60)` | ✓ |  |
| `pcdb206` | `varchar(50)` | ✓ |  |
| `pcdb220` | `varchar(80)` | ✓ |  |
| `pcdb222` | `varchar(60)` | ✓ |  |
| `pcdb224` | `varchar(60)` | ✓ |  |
| `pcdb226` | `varchar(40)` | ✓ |  |
| `noref` | `char(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pcdb308` | `varchar(30)` | ✓ |  |
| `pcdbnocause` | `varchar(17)` | ✓ |  |
| `pcdb380` | `varchar(80)` | ✓ |  |
| `pcdb382` | `smalldatetime` | ✓ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdb386` | `smalldatetime` | ✓ |  |
| `pcdbcodenat` | `varchar(6)` | ✓ |  |
| `pcdbnoch` | `varchar(20)` | ✓ |  |
| `pcdbdatech` | `smalldatetime` | ✓ |  |
| `pcdbtotal` | `decimal(15, 2)` | ✓ |  |
| `pcdbidapp` | `varchar(10)` | ✓ |  |
| `pcdbidsai` | `varchar(10)` | ✓ |  |
| `pcdbdatesai` | `smalldatetime` | ✓ |  |
| `pcdbdateapp` | `smalldatetime` | ✓ |  |
| `pcdbdateappspec` | `smalldatetime` | ✓ |  |
| `pcdbdateprpmnt` | `smalldatetime` | ✓ |  |
| `pcdbstatut` | `char(1)` | ✓ |  |
| `pcdbcoderairev` | `char(1)` | ✓ |  |
| `pcdbdateccj` | `smalldatetime` | ✓ |  |
| `pcdbdatefac` | `smalldatetime` | ✓ |  |
| `pcdbdatecsj` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `pcdbmontant` | `decimal(15, 2)` | ✓ |  |
| `pcdbmontantrecl` | `decimal(15, 2)` | ✓ |  |
| `pcdbavopay` | `char(1)` | ✓ |  |
| `pcdbtxtavis` | `varchar(5000)` | ✓ |  |
| `pcdbfacferme` | `char(1)` | ✓ |  |
| `pcdbfacpaye` | `char(2)` | ✓ |  |
| `pcdbmontcontrib` | `decimal(15, 2)` | ✓ |  |
| `pcdbvoletcontrib` | `char(1)` | ✓ |  |
| `pcdbraisannul` | `char(2)` | ✓ |  |
| `pcdbdateannul` | `smalldatetime` | ✓ |  |
| `pcdbinterets` | `decimal(15, 2)` | ✓ |  |
| `pcdblotfact` | `varchar(10)` | ✓ |  |
| `pcdblotpaie` | `varchar(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcdbart87` | `char(1)` | ✓ |  |
| `pcdbouvert` | `int` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdbcontcalc` | `decimal(8, 2)` | ✓ |  |
| `pcdbnote` | `varchar(5000)` | ✓ |  |
| `pcdbadverse` | `varchar(50)` | ✓ |  |
| `pcdbcour` | `varchar(50)` | ✓ |  |
| `pcdbdistrict` | `varchar(25)` | ✓ |  |
| `pcdbnomloi` | `varchar(255)` | ✓ |  |
| `pcdbarticle` | `varchar(25)` | ✓ |  |
| `pcdbcomavo` | `varchar(7050)` | ✓ |  |
| `pcdbcomccj` | `varchar(5000)` | ✓ |  |
| `pcdbpj` | `char(1)` | ✓ |  |
| `pcdbinterim` | `char(1)` | ✓ |  |
| `nodossier` | `varchar(17)` | ✗ |  |
| `periodecompt` | `char(7)` | ✗ |  |
| `pcdbfirme` | `varchar(150)` | ✓ |  |
| `pcdbnoTPS` | `varchar(25)` | ✓ |  |
| `pcdbnoTVQ` | `varchar(25)` | ✓ |  |
| `pcdbmtTPS` | `decimal(18, 2)` | ✓ |  |
| `pcdbmtTVQ` | `decimal(18, 2)` | ✓ |  |
| `OkDelete` | `bit` | ✓ |  |

### `honorstaLastVAvant220606`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✓ |  |
| `categorie` | `char(1)` | ✓ |  |
| `version` | `char(3)` | ✓ |  |

### `Suspens`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `column1` | `nvarchar(150)` | ✗ |  |
| `column2` | `nvarchar(50)` | ✗ |  |

### `_factureTMPRetro`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `noref` | `char(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pcdbcodenat` | `varchar(6)` | ✓ |  |
| `pcdbdatefac` | `smalldatetime` | ✓ |  |

### `honorstaLastVAvant231001`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✓ |  |
| `categorie` | `char(1)` | ✓ |  |
| `version` | `char(3)` | ✓ |  |

### `retro25`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(15)` | ✓ |  |
| `categorie` | `char(1)` | ✓ |  |
| `version` | `char(2)` | ✓ |  |

### `adminavo`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(6)` | ✗ |  |
| `annee` | `char(4)` | ✗ |  |
| `cumuldebut` | `decimal(9, 2)` | ✗ |  |
| `cumulfin` | `decimal(9, 2)` | ✗ |  |
| `cumulsecur` | `decimal(9, 2)` | ✗ |  |
| `art174` | `decimal(9, 2)` | ✗ |  |

### `_facturex`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `pcdb200` | `varchar(40)` | ✓ |  |
| `pcdb202` | `varchar(60)` | ✓ |  |
| `pcdb204` | `varchar(60)` | ✓ |  |
| `pcdb206` | `varchar(50)` | ✓ |  |
| `pcdb220` | `varchar(80)` | ✓ |  |
| `pcdb222` | `varchar(60)` | ✓ |  |
| `pcdb224` | `varchar(60)` | ✓ |  |
| `pcdb226` | `varchar(40)` | ✓ |  |
| `noref` | `char(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pcdb308` | `varchar(30)` | ✓ |  |
| `pcdbnocause` | `varchar(17)` | ✓ |  |
| `pcdb380` | `varchar(80)` | ✓ |  |
| `pcdb382` | `smalldatetime` | ✓ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdb386` | `smalldatetime` | ✓ |  |
| `pcdbcodenat` | `varchar(6)` | ✓ |  |
| `pcdbnoch` | `varchar(20)` | ✓ |  |
| `pcdbdatech` | `smalldatetime` | ✓ |  |
| `pcdbtotal` | `decimal(15, 2)` | ✓ |  |
| `pcdbidapp` | `varchar(10)` | ✓ |  |
| `pcdbidsai` | `varchar(10)` | ✓ |  |
| `pcdbdatesai` | `smalldatetime` | ✓ |  |
| `pcdbdateapp` | `smalldatetime` | ✓ |  |
| `pcdbdateappspec` | `smalldatetime` | ✓ |  |
| `pcdbdateprpmnt` | `smalldatetime` | ✓ |  |
| `pcdbstatut` | `char(1)` | ✓ |  |
| `pcdbcoderairev` | `char(1)` | ✓ |  |
| `pcdbdateccj` | `smalldatetime` | ✓ |  |
| `pcdbdatefac` | `smalldatetime` | ✓ |  |
| `pcdbdatecsj` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `pcdbmontant` | `decimal(15, 2)` | ✓ |  |
| `pcdbmontantrecl` | `decimal(15, 2)` | ✓ |  |
| `pcdbavopay` | `char(1)` | ✓ |  |
| `pcdbtxtavis` | `varchar(5000)` | ✓ |  |
| `pcdbfacferme` | `char(1)` | ✓ |  |
| `pcdbfacpaye` | `char(2)` | ✓ |  |
| `pcdbmontcontrib` | `decimal(15, 2)` | ✓ |  |
| `pcdbvoletcontrib` | `char(1)` | ✓ |  |
| `pcdbraisannul` | `char(2)` | ✓ |  |
| `pcdbdateannul` | `smalldatetime` | ✓ |  |
| `pcdbinterets` | `decimal(15, 2)` | ✓ |  |
| `pcdblotfact` | `varchar(10)` | ✓ |  |
| `pcdblotpaie` | `varchar(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcdbart87` | `char(1)` | ✓ |  |
| `pcdbouvert` | `int` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdbcontcalc` | `decimal(8, 2)` | ✓ |  |
| `pcdbnote` | `varchar(5000)` | ✓ |  |
| `pcdbadverse` | `varchar(50)` | ✓ |  |
| `pcdbcour` | `varchar(50)` | ✓ |  |
| `pcdbdistrict` | `varchar(25)` | ✓ |  |
| `pcdbnomloi` | `varchar(255)` | ✓ |  |
| `pcdbarticle` | `varchar(25)` | ✓ |  |
| `pcdbcomavo` | `varchar(7050)` | ✓ |  |
| `pcdbcomccj` | `varchar(5000)` | ✓ |  |
| `pcdbpj` | `char(1)` | ✓ |  |
| `pcdbinterim` | `char(1)` | ✓ |  |
| `nodossier` | `varchar(17)` | ✗ |  |
| `periodecompt` | `char(7)` | ✗ |  |
| `pcdbfirme` | `varchar(150)` | ✓ |  |
| `pcdbnoTPS` | `varchar(25)` | ✓ |  |
| `pcdbnoTVQ` | `varchar(25)` | ✓ |  |
| `pcdbmtTPS` | `decimal(18, 2)` | ✓ |  |
| `pcdbmtTVQ` | `decimal(18, 2)` | ✓ |  |
| `OkDelete` | `bit` | ✓ |  |
| `pcdbnoteRemb` | `varchar(5000)` | ✓ |  |
| `pcdbauteurNRemb` | `varchar(200)` | ✓ |  |

### `_TDominic`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `Date doc#` | `datetime` | ✓ |  |
| `facturerev` | `varchar(50)` | ✓ |  |
| `DateCh` | `datetime` | ✓ |  |
| `$` | `float` | ✓ |  |
| `F5` | `nvarchar(255)` | ✓ |  |
| `F6` | `nvarchar(255)` | ✓ |  |
| `F7` | `nvarchar(255)` | ✓ |  |
| `F8` | `nvarchar(255)` | ✓ |  |

### `_tSuspens-20240814`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✓ |  |
| `norevision` | `int` | ✓ |  |

### `adminavo210121`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `code` | `char(6)` | ✗ |  |
| `annee` | `char(4)` | ✗ |  |
| `cumuldebut` | `decimal(9, 2)` | ✗ |  |
| `cumulfin` | `decimal(9, 2)` | ✗ |  |
| `cumulsecur` | `decimal(9, 2)` | ✗ |  |
| `art174` | `decimal(9, 2)` | ✗ |  |

### `avocrim`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `pcdbcodeavoman` | `char(6)` | ✗ |  |
| `natgra002` | `char(2)` | ✗ |  |
| `tothon` | `decimal(15, 2)` | ✗ |  |

### `avoparmatiere`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `pcdbcodeavoman` | `char(6)` | ✗ |  |
| `natgra002` | `char(2)` | ✗ |  |
| `hontot` | `decimal(15, 2)` | ✗ |  |

### `Bug2905$`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofactrev` | `varchar(16)` | ✓ |  |

### `ConfigVals`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `iConfigID` | `int` | ✓ |  |
| `cCategory` | `varchar(20)` | ✓ |  |
| `cGroupCode` | `varchar(40)` | ✓ |  |
| `cValue` | `varchar(255)` | ✓ |  |
| `cLinkVal` | `varchar(150)` | ✓ |  |
| `cAvisPaiement` | `bit` | ✗ |  |
| `cRapportMens` | `bit` | ✗ |  |

### `debourselog`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(12)` | ✓ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pcdecodedeb` | `char(4)` | ✗ |  |
| `pcdedatedeb` | `smalldatetime` | ✗ |  |
| `pcdemontreclame` | `decimal(15, 2)` | ✗ |  |
| `pcdemontpaye` | `decimal(15, 2)` | ✗ |  |
| `pcdecomm` | `varchar(100)` | ✓ |  |
| `pcdestatut` | `char(1)` | ✓ |  |
| `pcdedatestatut` | `smalldatetime` | ✓ |  |
| `pcdeapp` | `int` | ✓ |  |
| `pcdedateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdenoseq` | `int` | ✓ |  |
| `pcdeexpert` | `varchar(6)` | ✓ |  |

### `Equivalence`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `cMnemonique` | `varchar(15)` | ✗ |  |
| `cCateg` | `char(4)` | ✗ |  |
| `cVersion` | `char(3)` | ✓ |  |
| `nTarif` | `decimal(15, 2)` | ✗ |  |
| `cEquivmnemo` | `varchar(15)` | ✓ |  |
| `cEquivcateg` | `char(4)` | ✓ |  |
| `cEquivversion` | `char(3)` | ✓ |  |
| `nEquivtarif` | `decimal(15, 2)` | ✓ |  |

### `equivalence2000`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `cMnemonique` | `varchar(15)` | ✗ |  |
| `cCateg` | `char(4)` | ✗ |  |
| `cVersion` | `char(3)` | ✓ |  |
| `nTarif` | `decimal(15, 2)` | ✗ |  |
| `cEquivmnemo` | `varchar(15)` | ✓ |  |
| `cEquivcateg` | `char(4)` | ✓ |  |
| `cEquivversion` | `char(3)` | ✓ |  |
| `nEquivtarif` | `decimal(15, 2)` | ✓ |  |

### `Equivalence2017`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `cMnemonique` | `varchar(20)` | ✗ |  |
| `cCateg` | `char(4)` | ✗ |  |
| `cVersion` | `char(3)` | ✓ |  |
| `nTarif` | `decimal(15, 2)` | ✗ |  |
| `cEquivmnemo` | `varchar(20)` | ✓ |  |
| `cEquivcateg` | `char(4)` | ✓ |  |
| `cEquivversion` | `char(3)` | ✓ |  |
| `nEquivtarif` | `decimal(15, 2)` | ✓ |  |
| `description` | `varchar(100)` | ✓ |  |
| `datedebut` | `smalldatetime` | ✓ |  |
| `datefin` | `smalldatetime` | ✓ |  |
| `forfait` | `char(1)` | ✓ |  |
| `mnemoforfait` | `varchar(10)` | ✓ |  |
| `equivalence` | `varchar(15)` | ✓ |  |

### `Equivalence2022`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `cMnemonique` | `varchar(15)` | ✗ |  |
| `cCateg` | `char(4)` | ✗ |  |
| `cVersion` | `char(3)` | ✓ |  |
| `nTarif` | `decimal(15, 2)` | ✗ |  |
| `cEquivmnemo` | `varchar(15)` | ✓ |  |
| `cEquivcateg` | `char(4)` | ✓ |  |
| `cEquivversion` | `char(3)` | ✓ |  |
| `nEquivtarif` | `decimal(15, 2)` | ✓ |  |

### `Equivalence2024`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `cMnemonique` | `varchar(15)` | ✗ |  |
| `cCateg` | `char(4)` | ✗ |  |
| `cVersion` | `char(3)` | ✓ |  |
| `nTarif` | `decimal(15, 2)` | ✗ |  |
| `cEquivmnemo` | `varchar(15)` | ✓ |  |
| `cEquivcateg` | `char(4)` | ✓ |  |
| `cEquivversion` | `char(3)` | ✓ |  |
| `nEquivtarif` | `decimal(15, 2)` | ✓ |  |

### `etats`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `trimestre` | `varchar(8)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |
| `a0506` | `money` | ✓ |  |
| `a0607` | `money` | ✓ |  |
| `a0708` | `money` | ✓ |  |
| `a0809` | `money` | ✓ |  |
| `a0910` | `money` | ✓ |  |
| `a1011` | `money` | ✓ |  |
| `a1112` | `money` | ✓ |  |
| `a1213` | `money` | ✓ |  |
| `a1314` | `money` | ✓ |  |
| `a1415` | `money` | ✓ |  |
| `a1516` | `money` | ✗ |  |
| `a1617` | `money` | ✗ |  |
| `a1718` | `money` | ✗ |  |
| `a1819` | `money` | ✗ |  |
| `a1920` | `money` | ✗ |  |
| `a2021` | `money` | ✗ |  |
| `a2122` | `money` | ✗ |  |
| `a2223` | `money` | ✗ |  |
| `a2324` | `money` | ✗ |  |
| `a2425` | `money` | ✗ |  |
| `a2526` | `money` | ✗ |  |
| `a2627` | `money` | ✗ |  |
| `a2728` | `money` | ✗ |  |
| `a2829` | `money` | ✗ |  |
| `a2930` | `money` | ✗ |  |

### `etats150409`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |
| `a0506` | `money` | ✓ |  |
| `a0607` | `money` | ✓ |  |
| `a0708` | `money` | ✓ |  |
| `a0809` | `money` | ✓ |  |

### `etatsbackup`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |
| `a0506` | `money` | ✓ |  |
| `a0607` | `money` | ✓ |  |
| `a0708` | `money` | ✓ |  |
| `a0809` | `money` | ✓ |  |
| `a0910` | `money` | ✓ |  |

### `etatscal`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `trimestre` | `varchar(8)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |
| `a0506` | `money` | ✓ |  |
| `a0607` | `money` | ✓ |  |
| `a0708` | `money` | ✓ |  |
| `a0809` | `money` | ✓ |  |
| `a0910` | `money` | ✓ |  |
| `a1011` | `money` | ✓ |  |
| `a1112` | `money` | ✗ |  |
| `a1213` | `money` | ✗ |  |
| `a1314` | `money` | ✗ |  |
| `a1415` | `money` | ✗ |  |

### `etatscompt`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✗ |  |
| `trimestre` | `varchar(8)` | ✗ |  |
| `av96` | `money` | ✗ |  |
| `a9697` | `money` | ✗ |  |
| `a9798` | `money` | ✗ |  |
| `a9899` | `money` | ✗ |  |
| `a9900` | `money` | ✗ |  |
| `a0001` | `money` | ✗ |  |
| `a0102` | `money` | ✗ |  |
| `a0203` | `money` | ✗ |  |
| `a0304` | `money` | ✗ |  |
| `a0405` | `money` | ✗ |  |
| `a0506` | `money` | ✗ |  |
| `a0607` | `money` | ✗ |  |
| `a0708` | `money` | ✗ |  |
| `a0809` | `money` | ✗ |  |
| `a0910` | `money` | ✗ |  |
| `a1011` | `money` | ✗ |  |
| `a1112` | `money` | ✗ |  |
| `a1213` | `money` | ✗ |  |
| `a1314` | `money` | ✗ |  |
| `a1415` | `money` | ✗ |  |
| `a1516` | `money` | ✗ |  |

### `etatsnature`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `nature` | `char(3)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |
| `a0506` | `money` | ✓ |  |
| `a0607` | `money` | ✓ |  |
| `a0708` | `money` | ✓ |  |

### `etatsnature150408`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `nature` | `char(3)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |
| `a0506` | `money` | ✓ |  |
| `a0607` | `money` | ✓ |  |
| `a0708` | `money` | ✓ |  |

### `etatsnature301104`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `nature` | `char(3)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |

### `etatsnature310305`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `nature` | `char(3)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |
| `a0506` | `money` | ✓ |  |
| `a0607` | `money` | ✓ |  |
| `a0708` | `money` | ✓ |  |

### `etatssept`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `trimestre` | `varchar(8)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |
| `a0506` | `money` | ✓ |  |
| `a0607` | `money` | ✓ |  |
| `a0708` | `money` | ✓ |  |
| `a0809` | `money` | ✓ |  |
| `a0910` | `money` | ✓ |  |
| `a1011` | `money` | ✓ |  |

### `etatsspec`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |

### `etatsverif`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |
| `a0506` | `money` | ✓ |  |
| `a0607` | `money` | ✓ |  |

### `etatsvolets310305`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nom` | `varchar(8)` | ✓ |  |
| `av96` | `money` | ✓ |  |
| `a9697` | `money` | ✓ |  |
| `a9798` | `money` | ✓ |  |
| `a9899` | `money` | ✓ |  |
| `a9900` | `money` | ✓ |  |
| `a0001` | `money` | ✓ |  |
| `a0102` | `money` | ✓ |  |
| `a0203` | `money` | ✓ |  |
| `a0304` | `money` | ✓ |  |
| `a0405` | `money` | ✓ |  |

### `extraction040609`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `no_facture` | `varchar(13)` | ✗ |  |
| `no_revision` | `int` | ✗ |  |
| `nom_avoc` | `varchar(40)` | ✓ |  |
| `nom_client` | `varchar(80)` | ✓ |  |
| `no_ref` | `varchar(11)` | ✓ |  |
| `no_region` | `varchar(2)` | ✗ |  |
| `no_bureau` | `varchar(2)` | ✗ |  |
| `no_seq_daj` | `varchar(12)` | ✓ |  |
| `no_cause` | `varchar(17)` | ✓ |  |
| `date_mandat` | `smalldatetime` | ✗ |  |
| `date_effec` | `smalldatetime` | ✓ |  |
| `code_nature` | `varchar(6)` | ✓ |  |
| `date_cheque` | `smalldatetime` | ✓ |  |
| `no_cheque` | `varchar(20)` | ✓ |  |
| `date_ccj` | `smalldatetime` | ✓ |  |
| `date_facture` | `smalldatetime` | ✓ |  |
| `total_fac` | `decimal(15, 2)` | ✓ |  |
| `date_fisc` | `varchar(4)` | ✓ |  |
| `statut` | `varchar(1)` | ✗ |  |
| `code_raison` | `varchar(1)` | ✓ |  |
| `code_avo_mand` | `varchar(6)` | ✗ |  |
| `mont_cont` | `decimal(15, 2)` | ✓ |  |
| `volet_cont` | `varchar(1)` | ✓ |  |
| `date_annul` | `smalldatetime` | ✓ |  |
| `interet` | `decimal(15, 2)` | ✓ |  |
| `cont_calc` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `km_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `km_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `no_fact_rev` | `varchar(16)` | ✗ |  |
| `conv_batch` | `varchar(2)` | ✓ |  |
| `periodecompt` | `char(7)` | ✓ |  |
| `dh_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `avo_ass_paye` | `decimal(18, 0)` | ✓ |  |

### `extraction200121`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `no_facture` | `varchar(13)` | ✗ |  |
| `no_revision` | `int` | ✗ |  |
| `nom_avoc` | `varchar(40)` | ✓ |  |
| `nom_client` | `varchar(80)` | ✓ |  |
| `no_ref` | `varchar(11)` | ✓ |  |
| `no_region` | `varchar(2)` | ✗ |  |
| `no_bureau` | `varchar(2)` | ✗ |  |
| `no_seq_daj` | `varchar(12)` | ✓ |  |
| `no_cause` | `varchar(17)` | ✓ |  |
| `date_mandat` | `smalldatetime` | ✗ |  |
| `date_effec` | `smalldatetime` | ✓ |  |
| `code_nature` | `varchar(6)` | ✓ |  |
| `date_cheque` | `smalldatetime` | ✓ |  |
| `no_cheque` | `varchar(20)` | ✓ |  |
| `date_ccj` | `smalldatetime` | ✓ |  |
| `date_facture` | `smalldatetime` | ✓ |  |
| `total_fac` | `decimal(15, 2)` | ✓ |  |
| `date_fisc` | `varchar(4)` | ✓ |  |
| `statut` | `varchar(1)` | ✗ |  |
| `code_raison` | `varchar(1)` | ✓ |  |
| `code_avo_mand` | `varchar(6)` | ✗ |  |
| `mont_cont` | `decimal(15, 2)` | ✓ |  |
| `volet_cont` | `varchar(1)` | ✓ |  |
| `date_annul` | `smalldatetime` | ✓ |  |
| `interet` | `decimal(15, 2)` | ✓ |  |
| `cont_calc` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `km_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `km_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `no_fact_rev` | `varchar(16)` | ✗ |  |
| `conv_batch` | `varchar(2)` | ✓ |  |
| `periodecompt` | `char(7)` | ✓ |  |
| `dh_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `avo_ass_paye` | `decimal(18, 0)` | ✓ |  |
| `tps` | `decimal(18, 2)` | ✓ |  |
| `tvq` | `decimal(18, 2)` | ✓ |  |
| `nt174` | `decimal(15, 2)` | ✓ |  |

### `extraction2007`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `no_facture` | `varchar(13)` | ✗ |  |
| `no_revision` | `int` | ✗ |  |
| `nom_avoc` | `varchar(40)` | ✓ |  |
| `nom_client` | `varchar(80)` | ✓ |  |
| `no_ref` | `varchar(11)` | ✓ |  |
| `no_region` | `varchar(2)` | ✗ |  |
| `no_bureau` | `varchar(2)` | ✗ |  |
| `no_seq_daj` | `varchar(12)` | ✓ |  |
| `no_cause` | `varchar(17)` | ✓ |  |
| `date_mandat` | `smalldatetime` | ✗ |  |
| `date_effec` | `smalldatetime` | ✓ |  |
| `code_nature` | `varchar(6)` | ✓ |  |
| `date_cheque` | `smalldatetime` | ✓ |  |
| `no_cheque` | `varchar(20)` | ✓ |  |
| `date_ccj` | `smalldatetime` | ✓ |  |
| `date_facture` | `smalldatetime` | ✓ |  |
| `total_fac` | `decimal(15, 2)` | ✓ |  |
| `date_fisc` | `varchar(4)` | ✓ |  |
| `statut` | `varchar(1)` | ✗ |  |
| `code_raison` | `varchar(1)` | ✓ |  |
| `code_avo_mand` | `varchar(6)` | ✗ |  |
| `mont_cont` | `decimal(15, 2)` | ✓ |  |
| `volet_cont` | `varchar(1)` | ✓ |  |
| `date_annul` | `smalldatetime` | ✓ |  |
| `interet` | `decimal(15, 2)` | ✓ |  |
| `cont_calc` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `km_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `km_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `no_fact_rev` | `varchar(16)` | ✗ |  |
| `conv_batch` | `varchar(2)` | ✓ |  |
| `periodecompt` | `char(7)` | ✓ |  |
| `dh_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `avo_ass_paye` | `decimal(18, 0)` | ✓ |  |

### `extraction210121`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `no_facture` | `varchar(13)` | ✗ |  |
| `no_revision` | `int` | ✗ |  |
| `nom_avoc` | `varchar(40)` | ✓ |  |
| `nom_client` | `varchar(80)` | ✓ |  |
| `no_ref` | `varchar(11)` | ✓ |  |
| `no_region` | `varchar(2)` | ✗ |  |
| `no_bureau` | `varchar(2)` | ✗ |  |
| `no_seq_daj` | `varchar(12)` | ✓ |  |
| `no_cause` | `varchar(17)` | ✓ |  |
| `date_mandat` | `smalldatetime` | ✗ |  |
| `date_effec` | `smalldatetime` | ✓ |  |
| `code_nature` | `varchar(6)` | ✓ |  |
| `date_cheque` | `smalldatetime` | ✓ |  |
| `no_cheque` | `varchar(20)` | ✓ |  |
| `date_ccj` | `smalldatetime` | ✓ |  |
| `date_facture` | `smalldatetime` | ✓ |  |
| `total_fac` | `decimal(15, 2)` | ✓ |  |
| `date_fisc` | `varchar(4)` | ✓ |  |
| `statut` | `varchar(1)` | ✗ |  |
| `code_raison` | `varchar(1)` | ✓ |  |
| `code_avo_mand` | `varchar(6)` | ✗ |  |
| `mont_cont` | `decimal(15, 2)` | ✓ |  |
| `volet_cont` | `varchar(1)` | ✓ |  |
| `date_annul` | `smalldatetime` | ✓ |  |
| `interet` | `decimal(15, 2)` | ✓ |  |
| `cont_calc` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `km_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `km_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `no_fact_rev` | `varchar(16)` | ✗ |  |
| `conv_batch` | `varchar(2)` | ✓ |  |
| `periodecompt` | `char(7)` | ✓ |  |
| `dh_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `avo_ass_paye` | `decimal(18, 0)` | ✓ |  |
| `tps` | `decimal(18, 2)` | ✓ |  |
| `tvq` | `decimal(18, 2)` | ✓ |  |
| `nt174` | `decimal(15, 2)` | ✓ |  |

### `extractionold`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `no_facture` | `varchar(13)` | ✗ |  |
| `no_revision` | `int` | ✗ |  |
| `nom_avoc` | `varchar(40)` | ✓ |  |
| `nom_client` | `varchar(80)` | ✓ |  |
| `no_ref` | `varchar(11)` | ✓ |  |
| `no_region` | `varchar(2)` | ✗ |  |
| `no_bureau` | `varchar(2)` | ✗ |  |
| `no_seq_daj` | `varchar(12)` | ✓ |  |
| `no_cause` | `varchar(17)` | ✓ |  |
| `date_mandat` | `smalldatetime` | ✗ |  |
| `date_effec` | `smalldatetime` | ✓ |  |
| `code_nature` | `varchar(6)` | ✓ |  |
| `date_cheque` | `smalldatetime` | ✓ |  |
| `no_cheque` | `varchar(20)` | ✓ |  |
| `date_ccj` | `smalldatetime` | ✓ |  |
| `date_facture` | `smalldatetime` | ✓ |  |
| `total_fac` | `decimal(15, 2)` | ✓ |  |
| `date_fisc` | `varchar(4)` | ✓ |  |
| `statut` | `varchar(1)` | ✗ |  |
| `code_raison` | `varchar(1)` | ✓ |  |
| `code_avo_mand` | `varchar(6)` | ✗ |  |
| `mont_cont` | `decimal(15, 2)` | ✓ |  |
| `volet_cont` | `varchar(1)` | ✓ |  |
| `date_annul` | `smalldatetime` | ✓ |  |
| `interet` | `decimal(15, 2)` | ✓ |  |
| `cont_calc` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `hon_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `deb_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `km_tot_recl` | `decimal(15, 2)` | ✓ |  |
| `km_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `no_fact_rev` | `varchar(16)` | ✗ |  |
| `conv_batch` | `varchar(2)` | ✓ |  |
| `periodecompt` | `char(7)` | ✓ |  |
| `dh_tot_paye` | `decimal(15, 2)` | ✓ |  |
| `avo_ass_paye` | `decimal(18, 0)` | ✓ |  |
| `tps` | `decimal(18, 2)` | ✓ |  |
| `tvq` | `decimal(18, 2)` | ✓ |  |

### `facrefer`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `reference` | `varchar(13)` | ✗ |  |
| `convbatch` | `char(2)` | ✓ |  |

### `facturelog`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✓ |  |
| `pcdb200` | `varchar(40)` | ✓ |  |
| `pcdb202` | `varchar(60)` | ✓ |  |
| `pcdb204` | `varchar(60)` | ✓ |  |
| `pcdb206` | `varchar(50)` | ✓ |  |
| `pcdb220` | `varchar(80)` | ✓ |  |
| `pcdb222` | `varchar(60)` | ✓ |  |
| `pcdb224` | `varchar(60)` | ✓ |  |
| `pcdb226` | `varchar(40)` | ✓ |  |
| `noref` | `char(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pcdb308` | `varchar(30)` | ✓ |  |
| `pcdbnocause` | `varchar(17)` | ✓ |  |
| `pcdb380` | `varchar(80)` | ✓ |  |
| `pcdb382` | `smalldatetime` | ✓ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdb386` | `smalldatetime` | ✓ |  |
| `pcdbcodenat` | `varchar(6)` | ✓ |  |
| `pcdbnoch` | `varchar(20)` | ✓ |  |
| `pcdbdatech` | `smalldatetime` | ✓ |  |
| `pcdbtotal` | `decimal(15, 2)` | ✓ |  |
| `pcdbidapp` | `varchar(10)` | ✓ |  |
| `pcdbidsai` | `varchar(10)` | ✓ |  |
| `pcdbdatesai` | `smalldatetime` | ✓ |  |
| `pcdbdateapp` | `smalldatetime` | ✓ |  |
| `pcdbdateappspec` | `smalldatetime` | ✓ |  |
| `pcdbdateprpmnt` | `smalldatetime` | ✓ |  |
| `pcdbstatut` | `char(1)` | ✓ |  |
| `pcdbcoderairev` | `char(1)` | ✓ |  |
| `pcdbdateccj` | `smalldatetime` | ✓ |  |
| `pcdbdatefac` | `smalldatetime` | ✓ |  |
| `pcdbdatecsj` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `pcdbmontant` | `decimal(15, 2)` | ✓ |  |
| `pcdbmontantrecl` | `decimal(15, 2)` | ✓ |  |
| `pcdbavopay` | `char(1)` | ✓ |  |
| `pcdbtxtavis` | `varchar(5000)` | ✓ |  |
| `pcdbfacferme` | `char(1)` | ✓ |  |
| `pcdbfacpaye` | `char(2)` | ✓ |  |
| `pcdbmontcontrib` | `decimal(15, 2)` | ✓ |  |
| `pcdbvoletcontrib` | `char(1)` | ✓ |  |
| `pcdbraisannul` | `char(2)` | ✓ |  |
| `pcdbdateannul` | `smalldatetime` | ✓ |  |
| `pcdbinterets` | `decimal(15, 2)` | ✓ |  |
| `pcdblotfact` | `varchar(10)` | ✓ |  |
| `pcdblotpaie` | `varchar(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcdbart87` | `char(1)` | ✓ |  |
| `pcdbouvert` | `int` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✓ |  |
| `pcdbcontcalc` | `decimal(8, 2)` | ✓ |  |
| `pcdbnote` | `varchar(5000)` | ✓ |  |
| `pcdbadverse` | `varchar(50)` | ✓ |  |
| `pcdbcour` | `varchar(50)` | ✓ |  |
| `pcdbdistrict` | `varchar(25)` | ✓ |  |
| `pcdbnomloi` | `varchar(255)` | ✓ |  |
| `pcdbarticle` | `varchar(25)` | ✓ |  |
| `pcdbcomavo` | `varchar(7050)` | ✓ |  |
| `pcdbcomccj` | `varchar(5000)` | ✓ |  |
| `pcdbpj` | `char(1)` | ✓ |  |
| `pcdbinterim` | `char(1)` | ✓ |  |
| `nodossier` | `varchar(17)` | ✗ |  |
| `periodecompt` | `char(7)` | ✗ |  |
| `pcdbfirme` | `varchar(150)` | ✓ |  |
| `pcdbnoTPS` | `varchar(25)` | ✓ |  |
| `pcdbnoTVQ` | `varchar(25)` | ✓ |  |
| `pcdbmtTPS` | `decimal(18, 2)` | ✓ |  |
| `pcdbmtTVQ` | `decimal(18, 2)` | ✓ |  |

### `factureThemis`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `pcdb200` | `varchar(40)` | ✓ |  |
| `pcdb202` | `varchar(60)` | ✓ |  |
| `pcdb204` | `varchar(60)` | ✓ |  |
| `pcdb206` | `varchar(50)` | ✓ |  |
| `pcdb220` | `varchar(80)` | ✓ |  |
| `pcdb222` | `varchar(60)` | ✓ |  |
| `pcdb224` | `varchar(60)` | ✓ |  |
| `pcdb226` | `varchar(40)` | ✓ |  |
| `noref` | `char(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pcdb308` | `varchar(30)` | ✓ |  |
| `pcdbnocause` | `varchar(17)` | ✓ |  |
| `pcdb380` | `varchar(80)` | ✓ |  |
| `pcdb382` | `smalldatetime` | ✓ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdb386` | `smalldatetime` | ✓ |  |
| `pcdbcodenat` | `varchar(6)` | ✓ |  |
| `pcdbnoch` | `varchar(20)` | ✓ |  |
| `pcdbdatech` | `smalldatetime` | ✓ |  |
| `pcdbtotal` | `decimal(15, 2)` | ✓ |  |
| `pcdbidapp` | `varchar(10)` | ✓ |  |
| `pcdbidsai` | `varchar(10)` | ✓ |  |
| `pcdbdatesai` | `smalldatetime` | ✓ |  |
| `pcdbdateapp` | `smalldatetime` | ✓ |  |
| `pcdbdateappspec` | `smalldatetime` | ✓ |  |
| `pcdbdateprpmnt` | `smalldatetime` | ✓ |  |
| `pcdbstatut` | `char(1)` | ✓ |  |
| `pcdbcoderairev` | `char(1)` | ✓ |  |
| `pcdbdateccj` | `smalldatetime` | ✓ |  |
| `pcdbdatefac` | `smalldatetime` | ✓ |  |
| `pcdbdatecsj` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `pcdbmontant` | `decimal(15, 2)` | ✓ |  |
| `pcdbmontantrecl` | `decimal(15, 2)` | ✓ |  |
| `pcdbavopay` | `char(1)` | ✓ |  |
| `pcdbtxtavis` | `varchar(5000)` | ✓ |  |
| `pcdbfacferme` | `char(1)` | ✓ |  |
| `pcdbfacpaye` | `char(2)` | ✓ |  |
| `pcdbmontcontrib` | `decimal(15, 2)` | ✓ |  |
| `pcdbvoletcontrib` | `char(1)` | ✓ |  |
| `pcdbraisannul` | `char(2)` | ✓ |  |
| `pcdbdateannul` | `smalldatetime` | ✓ |  |
| `pcdbinterets` | `decimal(15, 2)` | ✓ |  |
| `pcdblotfact` | `varchar(10)` | ✓ |  |
| `pcdblotpaie` | `varchar(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcdbart87` | `char(1)` | ✓ |  |
| `pcdbouvert` | `int` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdbcontcalc` | `decimal(8, 2)` | ✓ |  |
| `pcdbnote` | `varchar(5000)` | ✓ |  |
| `pcdbadverse` | `varchar(50)` | ✓ |  |
| `pcdbcour` | `varchar(50)` | ✓ |  |
| `pcdbdistrict` | `varchar(25)` | ✓ |  |
| `pcdbnomloi` | `varchar(255)` | ✓ |  |
| `pcdbarticle` | `varchar(25)` | ✓ |  |
| `pcdbcomavo` | `varchar(7050)` | ✓ |  |
| `pcdbcomccj` | `varchar(5000)` | ✓ |  |
| `pcdbpj` | `char(1)` | ✓ |  |
| `pcdbinterim` | `char(1)` | ✓ |  |
| `nodossier` | `varchar(17)` | ✗ |  |
| `periodecompt` | `char(7)` | ✗ |  |
| `pcdbfirme` | `varchar(150)` | ✓ |  |
| `pcdbnoTPS` | `varchar(25)` | ✓ |  |
| `pcdbnoTVQ` | `varchar(25)` | ✓ |  |
| `pcdbmtTPS` | `decimal(18, 2)` | ✓ |  |
| `pcdbmtTVQ` | `decimal(18, 2)` | ✓ |  |
| `OkDelete` | `bit` | ✓ |  |

### `forfait`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `pcfoforfait` | `varchar(15)` | ✗ |  |
| `pcfodateserv` | `smalldatetime` | ✗ |  |
| `pcfoitem` | `varchar(30)` | ✗ |  |
| `pcfodateitem` | `smalldatetime` | ✗ |  |

### `FVIFacture`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofactrev` | `varchar(16)` | ✓ |  |
| `groupeid` | `varchar(16)` | ✓ |  |
| `daterecue` | `datetime` | ✓ |  |

### `FviPmj`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `iUpdateID` | `int` | ✓ |  |
| `cDatabase` | `nvarchar(15)` | ✓ |  |
| `cTable` | `nvarchar(15)` | ✓ |  |
| `cCle` | `nvarchar(255)` | ✓ |  |
| `cAction` | `nvarchar(1)` | ✓ |  |
| `dModif` | `smalldatetime` | ✓ |  |

### `FviPmjFact`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `iUpdateID` | `int` | ✓ |  |
| `cDatabase` | `nvarchar(15)` | ✓ |  |
| `cTable` | `nvarchar(15)` | ✓ |  |
| `cCle` | `nvarchar(255)` | ✓ |  |
| `cAction` | `nvarchar(1)` | ✓ |  |
| `dModif` | `smalldatetime` | ✓ |  |

### `FVIvsART52`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `cnofacture` | `varchar(15)` | ✗ |  |
| `cnorevision` | `char(2)` | ✗ |  |
| `cnocauseadd` | `varchar(255)` | ✓ |  |

### `Honoraire202206`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `nvarchar(50)` | ✗ |  |
| `categorie` | `nvarchar(50)` | ✓ |  |
| `version` | `tinyint` | ✓ |  |
| `description` | `nvarchar(100)` | ✗ |  |
| `tarif` | `smallint` | ✗ |  |
| `datedebut` | `datetime2(7)` | ✓ |  |
| `datefin` | `datetime2(7)` | ✓ |  |
| `forfait` | `nvarchar(50)` | ✓ |  |
| `mnemoforfait` | `nvarchar(50)` | ✓ |  |
| `equivalence` | `nvarchar(50)` | ✓ |  |
| `Colonne1` | `nvarchar(50)` | ✓ |  |

### `honorairlog`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pchodateserv` | `smalldatetime` | ✓ |  |
| `pchonotarif` | `varchar(20)` | ✗ |  |
| `pchoverstarif` | `char(3)` | ✗ |  |
| `pchocattarif` | `char(1)` | ✗ |  |
| `pchomontreclame` | `decimal(15, 2)` | ✗ |  |
| `pchomontpaye` | `decimal(15, 2)` | ✗ |  |
| `pchocomm` | `varchar(100)` | ✓ |  |
| `pchostatut` | `char(1)` | ✓ |  |
| `pchodatestatut` | `smalldatetime` | ✓ |  |
| `pchoapp` | `int` | ✓ |  |
| `pchodateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pchonoseq` | `int` | ✓ |  |
| `pchoraisnt` | `char(1)` | ✗ |  |

### `honorsta_2025-04-07`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✗ |  |
| `categorie` | `char(1)` | ✗ |  |
| `version` | `char(3)` | ✗ |  |
| `description` | `varchar(50)` | ✗ |  |
| `tarif` | `decimal(15, 2)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✓ |  |
| `forfait` | `char(1)` | ✓ |  |
| `mnemoforfait` | `varchar(10)` | ✓ |  |
| `equivalence` | `varchar(15)` | ✓ |  |
| `convbatchID` | `int` | ✓ |  |

### `honorsta2007`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(15)` | ✗ |  |
| `categorie` | `char(1)` | ✗ |  |
| `version` | `char(3)` | ✗ |  |
| `description` | `varchar(50)` | ✗ |  |
| `tarif` | `decimal(15, 2)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✓ |  |
| `forfait` | `char(1)` | ✓ |  |
| `mnemoforfait` | `varchar(10)` | ✓ |  |
| `equivalence` | `varchar(15)` | ✓ |  |

### `honorsta2017`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✗ |  |
| `categorie` | `char(1)` | ✗ |  |
| `version` | `char(3)` | ✗ |  |
| `description` | `varchar(100)` | ✗ |  |
| `tarif` | `decimal(15, 2)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✓ |  |
| `forfait` | `char(1)` | ✓ |  |
| `mnemoforfait` | `varchar(10)` | ✓ |  |
| `equivalence` | `varchar(20)` | ✓ |  |

### `honorsta2020`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✗ |  |
| `categorie` | `char(1)` | ✗ |  |
| `version` | `char(3)` | ✗ |  |
| `description` | `varchar(50)` | ✗ |  |
| `tarif` | `decimal(15, 2)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✓ |  |
| `forfait` | `char(1)` | ✓ |  |
| `mnemoforfait` | `varchar(10)` | ✓ |  |
| `equivalence` | `varchar(15)` | ✓ |  |

### `honorsta2022`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✗ |  |
| `categorie` | `char(1)` | ✗ |  |
| `version` | `char(3)` | ✗ |  |
| `description` | `varchar(50)` | ✗ |  |
| `tarif` | `decimal(15, 2)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✓ |  |
| `forfait` | `char(1)` | ✓ |  |
| `mnemoforfait` | `varchar(10)` | ✓ |  |
| `equivalence` | `varchar(15)` | ✓ |  |

### `honorsta2024`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✗ |  |
| `categorie` | `char(1)` | ✗ |  |
| `version` | `char(3)` | ✗ |  |
| `description` | `varchar(50)` | ✗ |  |
| `tarif` | `decimal(15, 2)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✓ |  |
| `forfait` | `char(1)` | ✓ |  |
| `mnemoforfait` | `varchar(10)` | ✓ |  |
| `equivalence` | `varchar(15)` | ✓ |  |
| `convbatchID` | `int` | ✓ |  |

### `honorstaNT2025`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✗ |  |
| `categorie` | `char(1)` | ✗ |  |
| `version` | `char(3)` | ✗ |  |
| `description` | `varchar(50)` | ✗ |  |
| `tarif` | `decimal(15, 2)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✓ |  |
| `forfait` | `char(1)` | ✓ |  |
| `mnemoforfait` | `varchar(10)` | ✓ |  |
| `equivalence` | `varchar(15)` | ✓ |  |

### `kilometrlog`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pckmorigdest` | `varchar(100)` | ✗ |  |
| `pckmdatekm` | `smalldatetime` | ✗ |  |
| `pckmnbkm` | `decimal(7, 2)` | ✓ |  |
| `pckmmontreclame` | `decimal(15, 2)` | ✗ |  |
| `pckmmontpaye` | `decimal(15, 2)` | ✗ |  |
| `pckmcomm` | `varchar(100)` | ✓ |  |
| `pckmstatut` | `char(1)` | ✓ |  |
| `pckmdatestatut` | `smalldatetime` | ✓ |  |
| `pckmapp` | `int` | ✓ |  |
| `pckmdateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pckmnoseq` | `int` | ✓ |  |

### `LogDestrFact`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `cnofactrev` | `char(16)` | ✗ |  |
| `cutilisateur` | `char(10)` | ✗ |  |
| `ddatedestr` | `datetime` | ✗ |  |
| `craison` | `varchar(100)` | ✗ |  |

### `LogModifFact`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `cnofactrev` | `char(16)` | ✗ |  |
| `cutilisateur` | `char(10)` | ✗ |  |
| `dmodif` | `datetime` | ✗ |  |
| `craison` | `varchar(100)` | ✗ |  |
| `indInteret` | `bit` | ✓ |  |

### `megaprocestarif`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `proces` | `char(20)` | ✗ |  |
| `dateservice` | `smalldatetime` | ✗ |  |
| `tarif` | `decimal(18, 0)` | ✗ |  |

### `memfrais`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `noref` | `varchar(11)` | ✓ |  |
| `montant` | `decimal(7, 2)` | ✓ |  |
| `noseq` | `int` | ✓ |  |
| `datecreation` | `smalldatetime` | ✓ |  |

### `nocauseslog`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pccanocause` | `varchar(17)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pccanature` | `char(6)` | ✓ |  |
| `pccadatefac` | `smalldatetime` | ✓ |  |
| `pccacodeavo` | `char(6)` | ✓ |  |
| `pccanomcli` | `varchar(60)` | ✓ |  |
| `pccastatut` | `char(2)` | ✓ |  |
| `pccaprincipale` | `char(1)` | ✓ |  |
| `pccacatregr` | `char(2)` | ✓ |  |
| `pccastatfac` | `char(1)` | ✓ |  |
| `pccaidutil` | `varchar(10)` | ✓ |  |
| `modifiepar` | `varchar(20)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |

### `nocausesRetro`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pccanocause` | `varchar(17)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pccanature` | `char(6)` | ✓ |  |
| `pccadatefac` | `smalldatetime` | ✓ |  |
| `pccacodeavo` | `char(6)` | ✓ |  |
| `pccanomcli` | `varchar(80)` | ✓ |  |
| `pccastatut` | `char(2)` | ✓ |  |
| `pccaprincipale` | `char(1)` | ✓ |  |
| `pccacatregr` | `char(2)` | ✓ |  |
| `pccastatfac` | `char(1)` | ✓ |  |
| `pccaidutil` | `varchar(10)` | ✓ |  |
| `modifiepar` | `varchar(20)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |

### `PcACom`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `Nodossier` | `varchar(15)` | ✓ |  |
| `noregbur` | `char(4)` | ✓ |  |
| `noseq` | `char(12)` | ✓ |  |
| `comm` | `varchar(1600)` | ✓ |  |

### `PcADos`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nodossier` | `varchar(15)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✓ |  |
| `pcatcodeavo` | `char(6)` | ✓ |  |
| `pcatdateemis` | `smalldatetime` | ✓ |  |
| `pcatdateouv` | `smalldatetime` | ✓ |  |
| `pcatnature` | `varchar(1600)` | ✓ |  |
| `pcatnomcli` | `varchar(40)` | ✓ |  |
| `pcatprenomcli` | `varchar(40)` | ✓ |  |
| `pcatcodenat` | `char(6)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcmtcont` | `decimal(18, 0)` | ✓ |  |
| `pcduree` | `text` | ✓ |  |
| `pcment` | `char(1)` | ✓ |  |
| `pcdtrev` | `varchar(8)` | ✓ |  |
| `pcdtreact` | `varchar(8)` | ✓ |  |
| `pccomm` | `varchar(1600)` | ✓ |  |

### `pcattest`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nodossier` | `varchar(15)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✓ |  |
| `pcatcodeavo` | `char(6)` | ✓ |  |
| `pcatdateemis` | `smalldatetime` | ✓ |  |
| `pcatdateouv` | `smalldatetime` | ✓ |  |
| `pcatnature` | `varchar(1600)` | ✓ |  |
| `pcatnomcli` | `varchar(40)` | ✓ |  |
| `pcatprenomcli` | `varchar(40)` | ✓ |  |
| `pcatcodenat` | `char(6)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcmtcont` | `decimal(18, 0)` | ✓ |  |
| `pcduree` | `text` | ✓ |  |
| `pcment` | `char(1)` | ✓ |  |
| `pcdtrev` | `varchar(8)` | ✓ |  |
| `pcdtreact` | `varchar(8)` | ✓ |  |
| `pccomm` | `varchar(1600)` | ✓ |  |

### `pcattestdouble`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nodossier` | `varchar(15)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✓ |  |
| `pcatcodeavo` | `char(6)` | ✓ |  |
| `pcatdateemis` | `smalldatetime` | ✓ |  |
| `pcatdateouv` | `smalldatetime` | ✓ |  |
| `pcatnature` | `varchar(1600)` | ✓ |  |
| `pcatnomcli` | `varchar(40)` | ✓ |  |
| `pcatprenomcli` | `varchar(40)` | ✓ |  |
| `pcatcodenat` | `char(6)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcmtcont` | `decimal(18, 0)` | ✓ |  |
| `pcduree` | `text` | ✓ |  |
| `pcment` | `char(1)` | ✓ |  |
| `pcdtrev` | `varchar(8)` | ✓ |  |
| `pcdtreact` | `varchar(8)` | ✓ |  |
| `pccomm` | `varchar(1600)` | ✓ |  |

### `pcKeys`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `region` | `char(2)` | ✗ |  |
| `nextkey` | `char(7)` | ✗ |  |

### `pclot`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `pclofact` | `varchar(10)` | ✓ |  |
| `pclostatut` | `varchar(1)` | ✓ |  |
| `pclodatedeb` | `smalldatetime` | ✓ |  |
| `pclodatefin` | `smalldatetime` | ✓ |  |
| `pclodatech` | `smalldatetime` | ✓ |  |
| `pclomontant` | `decimal(15, 2)` | ✓ |  |
| `pclonbfac` | `int` | ✓ |  |

### `pcpost`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `postseqnce` | `decimal(10, 0)` | ✓ |  |

### `PiecesJustificatives`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `iPieceID` | `int` | ✓ |  |
| `cNomFichier` | `varchar(250)` | ✗ |  |
| `iType` | `int` | ✓ |  |
| `cCommentaires` | `varchar(4000)` | ✓ |  |
| `cDetail` | `varchar(1000)` | ✓ |  |

### `PiecesRecues`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `char(13)` | ✓ |  |
| `norevision` | `int` | ✓ |  |
| `pcdbdateccj` | `datetime` | ✓ |  |
| `pcdbstatut` | `char(1)` | ✓ |  |
| `pcdbnoch` | `char(20)` | ✓ |  |
| `pcdbdatech` | `datetime` | ✓ |  |
| `pcdbidapp` | `char(10)` | ✓ |  |
| `daterecue` | `datetime` | ✓ |  |

### `pmjtest`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `iUpdateID` | `int` | ✓ |  |
| `cDatabase` | `nvarchar(15)` | ✓ |  |
| `cTable` | `nvarchar(15)` | ✓ |  |
| `cCle` | `nvarchar(255)` | ✓ |  |
| `cAction` | `nvarchar(1)` | ✓ |  |
| `dModif` | `smalldatetime` | ✓ |  |

### `refretro`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofactrev` | `varchar(16)` | ✗ |  |
| `reference` | `varchar(15)` | ✓ |  |

### `retrodemi`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✗ |  |
| `categorie` | `char(1)` | ✗ |  |
| `version` | `char(3)` | ✗ |  |
| `equivalence` | `varchar(15)` | ✓ |  |

### `suivi`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `nomclient` | `varchar(40)` | ✓ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `noregbur` | `char(4)` | ✓ |  |
| `codeavocat` | `char(6)` | ✗ |  |
| `nomavocat` | `varchar(50)` | ✓ |  |
| `datecheque` | `datetime` | ✓ |  |
| `nbrevisions` | `char(1)` | ✓ |  |
| `requerant` | `varchar(40)` | ✓ |  |
| `region` | `char(2)` | ✗ |  |
| `raison` | `varchar(15)` | ✓ |  |
| `dateenvoi` | `datetime` | ✓ |  |
| `dateretour` | `datetime` | ✓ |  |
| `idutil` | `varchar(50)` | ✓ |  |

### `suiviold`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `nomclient` | `varchar(40)` | ✓ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `noregbur` | `char(4)` | ✓ |  |
| `codeavocat` | `char(6)` | ✗ |  |
| `nomavocat` | `varchar(50)` | ✓ |  |
| `datecheque` | `datetime` | ✓ |  |
| `nbrevisions` | `char(1)` | ✓ |  |
| `requerant` | `varchar(40)` | ✓ |  |
| `region` | `char(2)` | ✗ |  |
| `raison` | `varchar(15)` | ✓ |  |
| `dateenvoi` | `datetime` | ✓ |  |
| `dateretour` | `datetime` | ✓ |  |
| `idutil` | `varchar(50)` | ✓ |  |

### `Tampon_Honosta`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `varchar(20)` | ✗ |  |
| `categorie` | `char(1)` | ✗ |  |
| `version` | `char(3)` | ✗ |  |
| `description` | `varchar(50)` | ✗ |  |
| `tarif` | `decimal(15, 2)` | ✗ |  |
| `datedebut` | `smalldatetime` | ✗ |  |
| `datefin` | `smalldatetime` | ✓ |  |
| `forfait` | `char(1)` | ✓ |  |
| `mnemoforfait` | `varchar(10)` | ✓ |  |
| `equivalence` | `varchar(15)` | ✓ |  |

### `tAvocatMontant`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `CODE` | `varchar(6)` | ✓ |  |
| `MONTANT` | `varchar(50)` | ✓ |  |
| `Colonne 2` | `varchar(50)` | ✓ |  |

### `tAvoException`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `AvoException` | `varchar(6)` | ✗ | 🔑 |
| `DateInsert` | `datetime` | ✗ |  |
| `UserInserted` | `varchar(50)` | ✓ |  |

### `Tb_nbFactureT56AetB`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `periode` | `nvarchar(50)` | ✓ |  |
| `nbTotalFacture` | `bigint` | ✓ |  |
| `nbT56UneFois` | `bigint` | ✓ |  |
| `nbT56DeuxFois` | `bigint` | ✓ |  |

### `tCNException`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `CodeException` | `char(5)` | ✗ | 🔑 |
| `DateInsert` | `datetime` | ✗ |  |
| `UserInserted` | `varchar(50)` | ✓ |  |

### `tdebourse_avant_2000`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(12)` | ✓ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pcdecodedeb` | `char(4)` | ✗ |  |
| `pcdedatedeb` | `smalldatetime` | ✗ |  |
| `pcdemontreclame` | `decimal(15, 2)` | ✗ |  |
| `pcdemontpaye` | `decimal(15, 2)` | ✗ |  |
| `pcdecomm` | `varchar(100)` | ✓ |  |
| `pcdestatut` | `char(1)` | ✓ |  |
| `pcdedatestatut` | `smalldatetime` | ✓ |  |
| `pcdeapp` | `int` | ✓ |  |
| `pcdedateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdenoseq` | `int` | ✓ |  |
| `pcdeexpert` | `varchar(6)` | ✓ |  |

### `tdebourse_avant_2005`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(12)` | ✓ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pcdecodedeb` | `char(4)` | ✗ |  |
| `pcdedatedeb` | `smalldatetime` | ✗ |  |
| `pcdemontreclame` | `decimal(15, 2)` | ✗ |  |
| `pcdemontpaye` | `decimal(15, 2)` | ✗ |  |
| `pcdecomm` | `varchar(100)` | ✓ |  |
| `pcdestatut` | `char(1)` | ✓ |  |
| `pcdedatestatut` | `smalldatetime` | ✓ |  |
| `pcdeapp` | `int` | ✓ |  |
| `pcdedateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdenoseq` | `int` | ✓ |  |
| `pcdeexpert` | `varchar(6)` | ✓ |  |

### `tdebourse_avant_2008`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(12)` | ✓ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pcdecodedeb` | `char(4)` | ✗ |  |
| `pcdedatedeb` | `smalldatetime` | ✗ |  |
| `pcdemontreclame` | `decimal(15, 2)` | ✗ |  |
| `pcdemontpaye` | `decimal(15, 2)` | ✗ |  |
| `pcdecomm` | `varchar(100)` | ✓ |  |
| `pcdestatut` | `char(1)` | ✓ |  |
| `pcdedatestatut` | `smalldatetime` | ✓ |  |
| `pcdeapp` | `int` | ✓ |  |
| `pcdedateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdenoseq` | `int` | ✓ |  |
| `pcdeexpert` | `varchar(6)` | ✓ |  |

### `tdebourse_avant_2011`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(12)` | ✓ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pcdecodedeb` | `char(4)` | ✗ |  |
| `pcdedatedeb` | `smalldatetime` | ✗ |  |
| `pcdemontreclame` | `decimal(15, 2)` | ✗ |  |
| `pcdemontpaye` | `decimal(15, 2)` | ✗ |  |
| `pcdecomm` | `varchar(100)` | ✓ |  |
| `pcdestatut` | `char(1)` | ✓ |  |
| `pcdedatestatut` | `smalldatetime` | ✓ |  |
| `pcdeapp` | `int` | ✓ |  |
| `pcdedateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdenoseq` | `int` | ✓ |  |
| `pcdeexpert` | `varchar(6)` | ✓ |  |

### `Temp_extraction`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `no_ref` | `varchar(50)` | ✓ |  |
| `no_region` | `varchar(50)` | ✓ |  |
| `no_bureau` | `varchar(50)` | ✓ |  |
| `date_effec` | `smalldatetime` | ✓ |  |
| `pchodateserv` | `smalldatetime` | ✓ |  |
| `date_cheque` | `smalldatetime` | ✓ |  |
| `natgra002` | `varchar(50)` | ✓ |  |
| `code_nature` | `varchar(50)` | ✓ |  |
| `description` | `varchar(200)` | ✓ |  |
| `no_fact_rev` | `varchar(50)` | ✓ |  |

### `Temp_FactureDebourseExpert`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `no_region` | `nvarchar(2)` | ✓ |  |
| `no_facture` | `nvarchar(50)` | ✓ |  |
| `nom_avoc` | `nvarchar(50)` | ✓ |  |
| `date_cheque` | `smalldatetime` | ✓ |  |
| `hon_tot_paye` | `nvarchar(50)` | ✓ |  |
| `deb_tot_paye` | `nvarchar(50)` | ✓ |  |
| `expertise` | `nvarchar(50)` | ✓ |  |

### `tFactRefGroup`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `noregbur` | `char(4)` | ✓ |  |
| `noref` | `char(11)` | ✓ |  |
| `nofacture` | `varchar(13)` | ✓ |  |
| `pcdbdatefac` | `datetime` | ✓ |  |

### `tFactRetroTMP`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `pcdbidapp` | `varchar(10)` | ✓ |  |
| `pcdbfirme` | `varchar(150)` | ✓ |  |
| `pcdbnoTPS` | `varchar(25)` | ✓ |  |
| `pcdbnoTVQ` | `varchar(25)` | ✓ |  |

### `tfacture_avant_2005xx`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `pcdb200` | `varchar(40)` | ✓ |  |
| `pcdb202` | `varchar(60)` | ✓ |  |
| `pcdb204` | `varchar(60)` | ✓ |  |
| `pcdb206` | `varchar(50)` | ✓ |  |
| `pcdb220` | `varchar(80)` | ✓ |  |
| `pcdb222` | `varchar(60)` | ✓ |  |
| `pcdb224` | `varchar(60)` | ✓ |  |
| `pcdb226` | `varchar(40)` | ✓ |  |
| `noref` | `char(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pcdb308` | `varchar(30)` | ✓ |  |
| `pcdbnocause` | `varchar(17)` | ✓ |  |
| `pcdb380` | `varchar(80)` | ✓ |  |
| `pcdb382` | `smalldatetime` | ✓ |  |
| `pcdb384` | `smalldatetime` | ✓ |  |
| `pcdb386` | `smalldatetime` | ✓ |  |
| `pcdbcodenat` | `varchar(6)` | ✓ |  |
| `pcdbnoch` | `varchar(20)` | ✓ |  |
| `pcdbdatech` | `smalldatetime` | ✓ |  |
| `pcdbtotal` | `decimal(15, 2)` | ✓ |  |
| `pcdbidapp` | `varchar(10)` | ✓ |  |
| `pcdbidsai` | `varchar(10)` | ✓ |  |
| `pcdbdatesai` | `smalldatetime` | ✓ |  |
| `pcdbdateapp` | `smalldatetime` | ✓ |  |
| `pcdbdateappspec` | `smalldatetime` | ✓ |  |
| `pcdbdateprpmnt` | `smalldatetime` | ✓ |  |
| `pcdbstatut` | `char(1)` | ✓ |  |
| `pcdbcoderairev` | `char(1)` | ✓ |  |
| `pcdbdateccj` | `smalldatetime` | ✓ |  |
| `pcdbdatefac` | `smalldatetime` | ✓ |  |
| `pcdbdatecsj` | `smalldatetime` | ✓ |  |
| `pcdbcodeavoman` | `varchar(6)` | ✓ |  |
| `pcdbmontant` | `decimal(15, 2)` | ✓ |  |
| `pcdbmontantrecl` | `decimal(15, 2)` | ✓ |  |
| `pcdbavopay` | `char(1)` | ✓ |  |
| `pcdbtxtavis` | `varchar(5000)` | ✓ |  |
| `pcdbfacferme` | `char(1)` | ✓ |  |
| `pcdbfacpaye` | `char(2)` | ✓ |  |
| `pcdbmontcontrib` | `decimal(15, 2)` | ✓ |  |
| `pcdbvoletcontrib` | `char(1)` | ✓ |  |
| `pcdbraisannul` | `char(2)` | ✓ |  |
| `pcdbdateannul` | `smalldatetime` | ✓ |  |
| `pcdbinterets` | `decimal(15, 2)` | ✓ |  |
| `pcdblotfact` | `varchar(10)` | ✓ |  |
| `pcdblotpaie` | `varchar(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `pcdbart87` | `char(1)` | ✓ |  |
| `pcdbouvert` | `int` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pcdbcontcalc` | `decimal(8, 2)` | ✓ |  |
| `pcdbnote` | `varchar(5000)` | ✓ |  |
| `pcdbadverse` | `varchar(50)` | ✓ |  |
| `pcdbcour` | `varchar(50)` | ✓ |  |
| `pcdbdistrict` | `varchar(25)` | ✓ |  |
| `pcdbnomloi` | `varchar(255)` | ✓ |  |
| `pcdbarticle` | `varchar(25)` | ✓ |  |
| `pcdbcomavo` | `varchar(7050)` | ✓ |  |
| `pcdbcomccj` | `varchar(5000)` | ✓ |  |
| `pcdbpj` | `char(1)` | ✓ |  |
| `pcdbinterim` | `char(1)` | ✓ |  |
| `nodossier` | `varchar(17)` | ✗ |  |
| `periodecompt` | `char(7)` | ✗ |  |
| `pcdbfirme` | `varchar(150)` | ✓ |  |
| `pcdbnoTPS` | `varchar(25)` | ✓ |  |
| `pcdbnoTVQ` | `varchar(25)` | ✓ |  |
| `pcdbmtTPS` | `decimal(18, 2)` | ✓ |  |
| `pcdbmtTVQ` | `decimal(18, 2)` | ✓ |  |
| `OkDelete` | `bit` | ✓ |  |

### `thonorair_avant_2000`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pchodateserv` | `smalldatetime` | ✓ |  |
| `pchonotarif` | `varchar(20)` | ✗ |  |
| `pchoverstarif` | `char(3)` | ✗ |  |
| `pchocattarif` | `char(1)` | ✗ |  |
| `pchomontreclame` | `decimal(15, 2)` | ✗ |  |
| `pchomontpaye` | `decimal(15, 2)` | ✗ |  |
| `pchocomm` | `varchar(100)` | ✓ |  |
| `pchostatut` | `char(1)` | ✓ |  |
| `pchodatestatut` | `smalldatetime` | ✓ |  |
| `pchoapp` | `int` | ✓ |  |
| `pchodateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pchonoseq` | `int` | ✓ |  |
| `pchoraisnt` | `char(1)` | ✗ |  |

### `thonorair_avant_2005`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pchodateserv` | `smalldatetime` | ✓ |  |
| `pchonotarif` | `varchar(20)` | ✗ |  |
| `pchoverstarif` | `char(3)` | ✗ |  |
| `pchocattarif` | `char(1)` | ✗ |  |
| `pchomontreclame` | `decimal(15, 2)` | ✗ |  |
| `pchomontpaye` | `decimal(15, 2)` | ✗ |  |
| `pchocomm` | `varchar(100)` | ✓ |  |
| `pchostatut` | `char(1)` | ✓ |  |
| `pchodatestatut` | `smalldatetime` | ✓ |  |
| `pchoapp` | `int` | ✓ |  |
| `pchodateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pchonoseq` | `int` | ✓ |  |
| `pchoraisnt` | `char(1)` | ✗ |  |

### `thonorair_avant_2008`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pchodateserv` | `smalldatetime` | ✓ |  |
| `pchonotarif` | `varchar(20)` | ✗ |  |
| `pchoverstarif` | `char(3)` | ✗ |  |
| `pchocattarif` | `char(1)` | ✗ |  |
| `pchomontreclame` | `decimal(15, 2)` | ✗ |  |
| `pchomontpaye` | `decimal(15, 2)` | ✗ |  |
| `pchocomm` | `varchar(100)` | ✓ |  |
| `pchostatut` | `char(1)` | ✓ |  |
| `pchodatestatut` | `smalldatetime` | ✓ |  |
| `pchoapp` | `int` | ✓ |  |
| `pchodateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pchonoseq` | `int` | ✓ |  |
| `pchoraisnt` | `char(1)` | ✗ |  |

### `thonorair_avant_2011`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pchodateserv` | `smalldatetime` | ✓ |  |
| `pchonotarif` | `varchar(20)` | ✗ |  |
| `pchoverstarif` | `char(3)` | ✗ |  |
| `pchocattarif` | `char(1)` | ✗ |  |
| `pchomontreclame` | `decimal(15, 2)` | ✗ |  |
| `pchomontpaye` | `decimal(15, 2)` | ✗ |  |
| `pchocomm` | `varchar(100)` | ✓ |  |
| `pchostatut` | `char(1)` | ✓ |  |
| `pchodatestatut` | `smalldatetime` | ✓ |  |
| `pchoapp` | `int` | ✓ |  |
| `pchodateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pchonoseq` | `int` | ✓ |  |
| `pchoraisnt` | `char(1)` | ✗ |  |

### `tkilometr_avant_2000`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pckmorigdest` | `varchar(100)` | ✗ |  |
| `pckmdatekm` | `smalldatetime` | ✗ |  |
| `pckmnbkm` | `decimal(7, 2)` | ✓ |  |
| `pckmmontreclame` | `decimal(15, 2)` | ✗ |  |
| `pckmmontpaye` | `decimal(15, 2)` | ✗ |  |
| `pckmcomm` | `varchar(100)` | ✓ |  |
| `pckmstatut` | `char(1)` | ✓ |  |
| `pckmdatestatut` | `smalldatetime` | ✓ |  |
| `pckmapp` | `int` | ✓ |  |
| `pckmdateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pckmnoseq` | `int` | ✓ |  |

### `tkilometr_avant_2005`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pckmorigdest` | `varchar(100)` | ✗ |  |
| `pckmdatekm` | `smalldatetime` | ✗ |  |
| `pckmnbkm` | `decimal(7, 2)` | ✓ |  |
| `pckmmontreclame` | `decimal(15, 2)` | ✗ |  |
| `pckmmontpaye` | `decimal(15, 2)` | ✗ |  |
| `pckmcomm` | `varchar(100)` | ✓ |  |
| `pckmstatut` | `char(1)` | ✓ |  |
| `pckmdatestatut` | `smalldatetime` | ✓ |  |
| `pckmapp` | `int` | ✓ |  |
| `pckmdateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pckmnoseq` | `int` | ✓ |  |

### `tkilometr_avant_2008`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pckmorigdest` | `varchar(100)` | ✗ |  |
| `pckmdatekm` | `smalldatetime` | ✗ |  |
| `pckmnbkm` | `decimal(7, 2)` | ✓ |  |
| `pckmmontreclame` | `decimal(15, 2)` | ✗ |  |
| `pckmmontpaye` | `decimal(15, 2)` | ✗ |  |
| `pckmcomm` | `varchar(100)` | ✓ |  |
| `pckmstatut` | `char(1)` | ✓ |  |
| `pckmdatestatut` | `smalldatetime` | ✓ |  |
| `pckmapp` | `int` | ✓ |  |
| `pckmdateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pckmnoseq` | `int` | ✓ |  |

### `tkilometr_avant_2011`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pckmorigdest` | `varchar(100)` | ✗ |  |
| `pckmdatekm` | `smalldatetime` | ✗ |  |
| `pckmnbkm` | `decimal(7, 2)` | ✓ |  |
| `pckmmontreclame` | `decimal(15, 2)` | ✗ |  |
| `pckmmontpaye` | `decimal(15, 2)` | ✗ |  |
| `pckmcomm` | `varchar(100)` | ✓ |  |
| `pckmstatut` | `char(1)` | ✓ |  |
| `pckmdatestatut` | `smalldatetime` | ✓ |  |
| `pckmapp` | `int` | ✓ |  |
| `pckmdateapp` | `smalldatetime` | ✓ |  |
| `nocompte` | `char(10)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `pckmnoseq` | `int` | ✓ |  |

### `tmemfrais_avant_2000`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `noref` | `varchar(11)` | ✓ |  |
| `montant` | `decimal(7, 2)` | ✓ |  |
| `noseq` | `int` | ✓ |  |
| `datecreation` | `smalldatetime` | ✓ |  |

### `tmemfrais_avant_2005`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `noref` | `varchar(11)` | ✓ |  |
| `montant` | `decimal(7, 2)` | ✓ |  |
| `noseq` | `int` | ✓ |  |
| `datecreation` | `smalldatetime` | ✓ |  |

### `tmemfrais_avant_2008`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `noref` | `varchar(11)` | ✓ |  |
| `montant` | `decimal(7, 2)` | ✓ |  |
| `noseq` | `int` | ✓ |  |
| `datecreation` | `smalldatetime` | ✓ |  |

### `tmemfrais_avant_2011`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |
| `noref` | `varchar(11)` | ✓ |  |
| `montant` | `decimal(7, 2)` | ✓ |  |
| `noseq` | `int` | ✓ |  |
| `datecreation` | `smalldatetime` | ✓ |  |

### `tnocauses_avant_2000`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pccanocause` | `varchar(17)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pccanature` | `char(6)` | ✓ |  |
| `pccadatefac` | `smalldatetime` | ✓ |  |
| `pccacodeavo` | `char(6)` | ✓ |  |
| `pccanomcli` | `varchar(80)` | ✓ |  |
| `pccastatut` | `char(2)` | ✓ |  |
| `pccaprincipale` | `char(1)` | ✓ |  |
| `pccacatregr` | `char(2)` | ✓ |  |
| `pccastatfac` | `char(1)` | ✓ |  |
| `pccaidutil` | `varchar(10)` | ✓ |  |
| `modifiepar` | `varchar(20)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |

### `tnocauses_avant_2005`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pccanocause` | `varchar(17)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pccanature` | `char(6)` | ✓ |  |
| `pccadatefac` | `smalldatetime` | ✓ |  |
| `pccacodeavo` | `char(6)` | ✓ |  |
| `pccanomcli` | `varchar(80)` | ✓ |  |
| `pccastatut` | `char(2)` | ✓ |  |
| `pccaprincipale` | `char(1)` | ✓ |  |
| `pccacatregr` | `char(2)` | ✓ |  |
| `pccastatfac` | `char(1)` | ✓ |  |
| `pccaidutil` | `varchar(10)` | ✓ |  |
| `modifiepar` | `varchar(20)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |

### `tnocauses_avant_2008`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pccanocause` | `varchar(17)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pccanature` | `char(6)` | ✓ |  |
| `pccadatefac` | `smalldatetime` | ✓ |  |
| `pccacodeavo` | `char(6)` | ✓ |  |
| `pccanomcli` | `varchar(80)` | ✓ |  |
| `pccastatut` | `char(2)` | ✓ |  |
| `pccaprincipale` | `char(1)` | ✓ |  |
| `pccacatregr` | `char(2)` | ✓ |  |
| `pccastatfac` | `char(1)` | ✓ |  |
| `pccaidutil` | `varchar(10)` | ✓ |  |
| `modifiepar` | `varchar(20)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |

### `tnocauses_avant_2011`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `nofacture` | `varchar(13)` | ✗ |  |
| `norevision` | `int` | ✗ |  |
| `noref` | `varchar(11)` | ✗ |  |
| `noreg` | `char(2)` | ✗ |  |
| `nobur` | `char(2)` | ✗ |  |
| `noregbur` | `char(4)` | ✗ |  |
| `pccanocause` | `varchar(17)` | ✗ |  |
| `noseqdaj` | `varchar(12)` | ✓ |  |
| `pccanature` | `char(6)` | ✓ |  |
| `pccadatefac` | `smalldatetime` | ✓ |  |
| `pccacodeavo` | `char(6)` | ✓ |  |
| `pccanomcli` | `varchar(80)` | ✓ |  |
| `pccastatut` | `char(2)` | ✓ |  |
| `pccaprincipale` | `char(1)` | ✓ |  |
| `pccacatregr` | `char(2)` | ✓ |  |
| `pccastatfac` | `char(1)` | ✓ |  |
| `pccaidutil` | `varchar(10)` | ✓ |  |
| `modifiepar` | `varchar(20)` | ✓ |  |
| `convbatch` | `char(2)` | ✓ |  |
| `nofactrev` | `varchar(16)` | ✗ |  |

### `tPaiementBatch`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `PaiementBatchID` | `int` | ✓ | 🔑 |
| `DatePaiement` | `datetime` | ✗ |  |
| `DateDebut` | `date` | ✓ |  |
| `DateFin` | `date` | ✓ |  |
| `MntLimite` | `numeric(10, 2)` | ✓ |  |
| `HonorairLimite` | `numeric(10, 2)` | ✓ |  |
| `DebouseLimite` | `numeric(10, 2)` | ✓ |  |
| `KmLimite` | `numeric(10, 2)` | ✓ |  |
| `HonorairLignes` | `int` | ✓ |  |
| `FA` | `bit` | ✗ |  |
| `CodeNature` | `varchar(5)` | ✓ |  |
| `Suffixe` | `varchar(1)` | ✓ |  |
| `MntPaye` | `numeric(10, 2)` | ✓ |  |
| `FactSelect` | `int` | ✓ |  |
| `Utilisateur` | `varchar(50)` | ✓ |  |
| `CommAprob` | `varchar(max)` | ✓ |  |

### `tPaiementBatchDet`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `PaimentBatchDetID` | `int` | ✓ | 🔑 |
| `PaiementBatchID` | `int` | ✗ |  |
| `nofacture` | `varchar(13)` | ✓ |  |
| `norevision` | `varchar(2)` | ✓ |  |
| `codeavo` | `varchar(6)` | ✓ |  |
| `codenature` | `varchar(6)` | ✓ |  |
| `MntReclame` | `numeric(10, 2)` | ✓ |  |
| `HonReclame` | `numeric(10, 2)` | ✓ |  |
| `DebReclame` | `numeric(10, 2)` | ✓ |  |
| `KmReclame` | `numeric(10, 2)` | ✓ |  |
| `MntTPS` | `numeric(10, 2)` | ✓ |  |
| `MntTVQ` | `numeric(10, 2)` | ✓ |  |
| `MntTotal` | `numeric(10, 2)` | ✓ |  |
| `Statut` | `int` | ✓ |  |
| `Note` | `varchar(max)` | ✓ |  |

### `tParametre`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `ParametreID` | `int` | ✓ |  |
| `FolderFrom` | `varchar(500)` | ✓ |  |
| `ActionMD` | `char(1)` | ✓ |  |
| `FolderMove` | `varchar(500)` | ✓ |  |
| `YearsOld` | `int` | ✓ |  |
| `Avocats` | `char(1)` | ✓ |  |
| `NoAvocat` | `varchar(50)` | ✓ |  |
| `TimeExec` | `datetime` | ✓ |  |
| `Actif` | `bit` | ✓ |  |

### `tTarif2024`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `id` | `int` | ✓ |  |
| `mnemonique` | `varchar(20)` | ✓ |  |
| `categorie` | `char(1)` | ✓ |  |
| `version` | `char(3)` | ✓ |  |
| `description` | `varchar(50)` | ✓ |  |
| `tarif` | `decimal(15, 2)` | ✓ |  |
| `datedebut` | `datetime` | ✓ |  |
| `datefin` | `datetime` | ✓ |  |
| `forfait` | `char(1)` | ✓ |  |
| `mnemoforfait` | `varchar(10)` | ✓ |  |
| `equivalence` | `varchar(15)` | ✓ |  |
| `convbatchID` | `int` | ✓ |  |

### `tTarif2024Excel`

| Colonne | Type | Null | PK |
|---------|------|:----:|:--:|
| `mnemonique` | `nvarchar(255)` | ✓ |  |
| `categorie` | `nvarchar(255)` | ✓ |  |
| `version` | `nvarchar(255)` | ✓ |  |
| `description` | `nvarchar(255)` | ✓ |  |
| `tarif` | `float` | ✓ |  |
| `datedebut` | `datetime` | ✓ |  |
| `datefin` | `datetime` | ✓ |  |
| `forfait` | `nvarchar(255)` | ✓ |  |
| `mnemoforfait` | `nvarchar(255)` | ✓ |  |
| `equivalence` | `nvarchar(255)` | ✓ |  |
| `convbatchID` | `nvarchar(255)` | ✓ |  |

---
