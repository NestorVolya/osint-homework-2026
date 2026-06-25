# Gephi vs Neo4j Comparison

## Джерело

Порівняння базується на фактичних артефактах ДЗ-12:

- `data/raw/groupint_messages.csv`
- `data/nodes_with_communities.csv`
- `data/edges_endorsements.csv`
- `data/processed/nodes_clean.csv`
- `data/processed/edges_endorsements_clean.csv`
- Gephi-проєкти у `screenshots/*.gephi`

## Порівняння ролей інструментів

| Пункт | Neo4j | Gephi |
|---|---|---|
| Основна роль | сховище GroupInt scrape | візуалізація і графові метрики |
| Дані повідомлень | `Message` nodes: 15100 унікальних повідомлень | повідомлення не імпортувались у фінальний Gephi-граф |
| Текст повідомлень | 11781 повідомлень з непорожнім `text` | використано опосередковано через CSV exports |
| Граф каналів | `Group -> Group` через `ENDORSES` | імпортований `Group -> Group ENDORSES` граф |
| Вузли в graph export | 70 до очищення, 60 після conservative dedup | 70 у первинному Gephi export |
| Ребра в graph export | 68 до очищення, 58 після conservative dedup | 68 у первинному Gephi export |

## Метрики

| Метрика | Neo4j / export | Gephi / gephi-ai |
|---|---|---|
| Degree / weighted degree | доступні в `nodes_with_communities.csv` після Gephi export | обчислено у Gephi |
| PageRank | не рахувався як окремий Neo4j GDS artifact | обчислено Gephi / gephi-ai |
| Betweenness | не рахувався як окремий Neo4j GDS artifact | 0.0 для всіх вузлів |
| Modularity | не рахувався як окремий Neo4j GDS artifact | 3 класи у CSV; 4 після Gephi re-computation |

## Висновок

Neo4j підтверджує повноту джерельної бази: 15100 повідомлень і графові зв'язки GroupInt. Gephi підтверджує графову структуру мережі: hub-and-spoke endorsement-граф з домінантними hub-вузлами і без формальних bridge-вузлів за betweenness.

Обмеження: це не повне порівняння алгоритмів Neo4j GDS vs Gephi, бо Neo4j GDS-метрики окремо не запускались і не збережені як artifact.
