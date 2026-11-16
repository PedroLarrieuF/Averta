"""Query generation for national lead coverage."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import itertools

from utils.config_loader import get_settings
from utils.logging import get_logger
from utils.helpers import generate_id

logger = get_logger(__name__)


@dataclass
class QueryConfig:
    """Configuration for query generation."""
    segment: str
    keywords: List[str]
    variations: List[str]
    target_segments: List[str]
    priority: int = 1


class QueryGenerator:
    """Generates search queries for national coverage."""

    def __init__(self, config_path: Optional[str] = None):
        self.settings = get_settings()
        self.config_path = config_path
        self.icp_config = self._load_icp_config()
        self.brazil_config = self._load_brazil_config()
        self.generated_queries: Set[str] = set()

    def _load_icp_config(self) -> Dict:
        """Load ICP keywords configuration."""
        if self.config_path:
            path = Path(self.config_path)
        else:
            path = Path(__file__).parent.parent.parent / "config" / "icp_keywords.yaml"

        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def _load_brazil_config(self) -> Dict:
        """Load Brazil states configuration."""
        path = Path(__file__).parent.parent.parent / "config" / "brazil_states.yaml"

        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def get_priority_segments(self) -> List[QueryConfig]:
        """Get priority segments from ICP config."""
        segments = []

        priority_segments = self.icp_config.get('priority_segments', {})

        for segment_name, segment_data in priority_segments.items():
            keywords = segment_data.get('keywords', [])
            variations = segment_data.get('variations', [])
            target_segments = segment_data.get('segments_alvo', [])

            # Determine priority based on segment
            priority = 1
            if segment_name in ['distribuidoras', 'atacadistas', 'industrias']:
                priority = 1
            elif segment_name in ['farma_hospitalar', 'alimenticias', 'bebidas']:
                priority = 1
            elif segment_name in ['autopeças', 'material_construcao']:
                priority = 1
            elif segment_name in ['ecommerce_logistica', 'grande_volume']:
                priority = 2

            segments.append(QueryConfig(
                segment=segment_name,
                keywords=keywords,
                variations=variations,
                target_segments=target_segments,
                priority=priority
            ))

        return segments

    def get_states_by_priority(self, priority: int = None) -> List[Dict]:
        """Get states filtered by priority."""
        states = self.brazil_config.get('states', {})
        result = []

        for code, data in states.items():
            if priority is None or data.get('priority') == priority:
                result.append({
                    'code': code,
                    'name': data.get('name'),
                    'capital': data.get('capital'),
                    'priority': data.get('priority', 3),
                    'major_cities': data.get('major_cities', []),
                    'industrial_poles': data.get('industrial_poles', []),
                })

        # Sort by priority then name
        result.sort(key=lambda x: (x['priority'], x['name']))
        return result

    def get_cities_for_state(self, state_code: str, max_cities: int = None) -> List[str]:
        """Get major cities for a state."""
        states = self.brazil_config.get('states', {})
        state_data = states.get(state_code, {})
        cities = state_data.get('major_cities', [])

        if max_cities:
            cities = cities[:max_cities]

        return cities

    def get_industrial_poles_for_state(self, state_code: str) -> List[str]:
        """Get industrial poles for a state."""
        states = self.brazil_config.get('states', {})
        state_data = states.get(state_code, {})
        return state_data.get('industrial_poles', [])

    def generate_queries_for_state(
        self,
        state_code: str,
        segment_configs: List[QueryConfig] = None,
        max_queries: int = None
    ) -> List[str]:
        """Generate queries for a specific state."""
        if segment_configs is None:
            segment_configs = self.get_priority_segments()

        state_cities = self.get_cities_for_state(state_code)
        industrial_poles = self.get_industrial_poles_for_state(state_code)

        if not state_cities:
            logger.warning(f"No cities found for state {state_code}")
            return []

        queries = []
        templates = self.icp_config.get('base_queries_by_region', {}).get('templates', [])
        industrial_templates = self.icp_config.get('base_queries_by_region', {}).get('industrial_poles', [])

        # Get state name for queries
        state_name = self._get_state_name(state_code)

        for segment_config in segment_configs:
            # Use main keywords + variations
            all_terms = segment_config.keywords + segment_config.variations

            # Also use target segments as search terms
            all_terms.extend(segment_config.target_segments[:10])  # Limit to avoid explosion

            # Generate queries for major cities
            for city in state_cities[:10]:  # Limit cities per state
                for term in all_terms[:5]:  # Limit terms per city
                    for template in templates[:3]:  # Limit templates
                        query = template.format(
                            segment=term,
                            city=city,
                            state=state_code
                        )
                        queries.append(query)

            # Generate queries for industrial poles
            for pole in industrial_poles[:3]:
                for template in industrial_templates[:2]:
                    query = template.format(pole=pole, state=state_code)
                    queries.append(query)

        # Deduplicate
        queries = list(dict.fromkeys(queries))

        # Apply max limit
        if max_queries and len(queries) > max_queries:
            queries = queries[:max_queries]

        return queries

    def generate_all_queries(
        self,
        priorities: List[int] = None,
        max_per_state: int = None,
        max_total: int = None
    ) -> List[str]:
        """Generate queries for all states."""
        if priorities is None:
            priorities = [1, 2, 3]

        segment_configs = self.get_priority_segments()
        all_queries = []

        for priority in priorities:
            states = self.get_states_by_priority(priority)

            for state in states:
                state_code = state['code']
                state_queries = self.generate_queries_for_state(
                    state_code,
                    segment_configs,
                    max_queries=max_per_state
                )
                all_queries.extend(state_queries)

                logger.debug(f"Generated {len(state_queries)} queries for {state_code} (priority {priority})")

        # Deduplicate globally
        all_queries = list(dict.fromkeys(all_queries))

        # Apply total limit
        if max_total and len(all_queries) > max_total:
            all_queries = all_queries[:max_total]

        logger.info(f"Generated {len(all_queries)} total unique queries")
        return all_queries

    def generate_focused_queries(
        self,
        state_codes: List[str],
        segments: List[str] = None,
        max_per_state: int = 50
    ) -> List[str]:
        """Generate focused queries for specific states and segments."""
        segment_configs = self.get_priority_segments()

        if segments:
            segment_configs = [s for s in segment_configs if s.segment in segments]

        all_queries = []

        for state_code in state_codes:
            state_queries = self.generate_queries_for_state(
                state_code,
                segment_configs,
                max_queries=max_per_state
            )
            all_queries.extend(state_queries)

        # Deduplicate
        all_queries = list(dict.fromkeys(all_queries))

        logger.info(f"Generated {len(all_queries)} focused queries for {len(state_codes)} states")
        return all_queries

    def save_queries(self, queries: List[str], filename: str = None) -> str:
        """Save queries to file."""
        if filename is None:
            from datetime import datetime
            filename = f"queries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        output_dir = Path(self.settings.queries_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            for query in queries:
                f.write(f"{query}\n")

        logger.info(f"Saved {len(queries)} queries to {filepath}")
        return str(filepath)

    def load_queries(self, filename: str) -> List[str]:
        """Load queries from file."""
        filepath = Path(self.settings.queries_dir) / filename

        if not filepath.exists():
            logger.warning(f"Query file not found: {filepath}")
            return []

        with open(filepath, 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip()]

        logger.info(f"Loaded {len(queries)} queries from {filepath}")
        return queries

    def _get_state_name(self, code: str) -> str:
        """Get state name from code."""
        states = self.brazil_config.get('states', {})
        return states.get(code, {}).get('name', code)

    def get_query_stats(self, queries: List[str]) -> Dict[str, Any]:
        """Get statistics about generated queries."""
        stats = {
            'total': len(queries),
            'by_state': {},
            'by_segment': {},
            'unique_cities': set(),
        }

        for query in queries:
            # Try to extract state
            for state_code in self.brazil_config.get('states', {}).keys():
                if f" {state_code}" in query or f"{state_code}" == query.split()[-1]:
                    stats['by_state'][state_code] = stats['by_state'].get(state_code, 0) + 1
                    break

            # Extract cities (simplified)
            words = query.split()
            for word in words:
                if word[0].isupper() and len(word) > 2:
                    stats['unique_cities'].add(word)

        stats['unique_cities'] = len(stats['unique_cities'])
        return stats


def generate_queries_main(
    output_file: str = None,
    priorities: List[int] = None,
    max_per_state: int = None,
    max_total: int = None
) -> List[str]:
    """Main function to generate queries."""
    generator = QueryGenerator()
    queries = generator.generate_all_queries(
        priorities=priorities,
        max_per_state=max_per_state,
        max_total=max_total
    )

    if output_file:
        generator.save_queries(queries, output_file)

    return queries


if __name__ == "__main__":
    import sys

    # Simple CLI
    output = sys.argv[1] if len(sys.argv) > 1 else None
    queries = generate_queries_main(output_file=output)
    print(f"Generated {len(queries)} queries")