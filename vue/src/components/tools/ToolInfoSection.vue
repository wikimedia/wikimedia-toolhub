<template>
	<v-list class="tool-list-section">
		<v-list-item
			v-for="item in section"
			:key="item.title"
		>
			<v-list-item-content>
				<v-list-item-title
					class="mb-2"
				>
					{{ item.title }}
				</v-list-item-title>
				<v-list-item
					v-if="item.terms"
					class="flex-wrap"
				>
					<v-chip
						v-for="term in item.terms"
						:key="term.term"
						:to="termSearch( item.param, term.term )"
						:ripple="false"
						link
						outlined
						color="primary"
						class="ma-1"
					>
						{{ term.label }}
					</v-chip>
				</v-list-item>
				<template
					v-else-if="item.href && Array.isArray( item.href )"
				>
					<v-list-item
						v-for="( href, idx ) in item.href"
						:key="idx"
					>
						<v-list-item-subtitle>
							<a :href="href.url"
								target="_blank"
							>
								{{ href.url }}
							</a>
						</v-list-item-subtitle>
					</v-list-item>
				</template>
				<v-list-item
					v-else-if="item.href"
				>
					<v-list-item-subtitle>
						<a :href="item.href"
							target="_blank"
						>
							{{ item.value || item.href }}
						</a>
					</v-list-item-subtitle>
				</v-list-item>
				<v-list-item
					v-else-if="item.value && Array.isArray( item.value )"
					class="flex-wrap"
				>
					<v-chip
						v-for="value in item.value"
						:key="value"
						:ripple="false"
						outlined
						disabled
						class="ma-1 opacity-1"
					>
						{{ value }}
					</v-chip>
				</v-list-item>
				<v-list-item
					v-else-if="item.value"
				>
					{{ item.value }}
				</v-list-item>
			</v-list-item-content>
		</v-list-item>
	</v-list>
</template>

<script>
export default {
	name: 'ToolInfoSection',
	props: {
		section: {
			type: Array,
			default: null
		}
	},
	methods: {
		termSearch( param, term ) {
			const link = {
				name: 'search',
				query: {}
			};
			link.query[ param ] = term;
			return link;
		}
	}
};
</script>
