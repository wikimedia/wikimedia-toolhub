<template>
	<v-container>
		<v-row dense>
			<v-col cols="12">
				<v-card
					class="mx-auto"
					outlined
					elevation="1"
				>
					<div class="d-flex flex-no-wrap justify-space-between">
						<div>
							<h2 class="display-1 ma-4">
								{{ $t( 'welcomemessage' ) }}
							</h2>
							<v-card-subtitle>
								{{ $t( 'tagline' ) }}
							</v-card-subtitle>
							<v-card-text>
								More text would go here and tell people something
								awesome about Toolhub or how to get started using it.
							</v-card-text>
						</div>
						<v-avatar
							class="ma-3"
							size="125"
							tile
						>
							<v-img src="/static/img/logo-community.svg" />
						</v-avatar>
					</div>
				</v-card>
			</v-col>
		</v-row>
		<v-row
			justify="space-around"
		>
			<v-row v-for="tool in toolsList"
				:key="tool.id"
				class="shrink"
			>
				<v-card
					class="my-8"
					min-width="365"
					max-width="365"
					min-height="470"
				>
					<v-card-title
						class="flex-nowrap"
					>
						<v-icon
							v-if="!tool.icon"
							class="me-2"
							size="50"
						>
							mdi-tools
						</v-icon>
						<v-img
							v-if="tool.icon"
							class="me-2"
							:src="tool.icon.img"
							max-height="50"
							max-width="50"
						/>
						<div
							class="home-tool-title line-clamp"
						>
							{{ tool.title }}
						</div>
					</v-card-title>

					<v-card-text>
						<p>{{ tool.name }}</p>

						<div class="text--primary home-tool-desc line-clamp">
							{{ tool.description }}
						</div>

						<div class="my-4 subtitle-1">
							{{ $t( 'authors' ) }}: {{ tool.author }}
						</div>
					</v-card-text>

					<v-divider class="mx-4" />

					<v-card-text>
						<v-chip-group
							v-if="tool.keywords"
							active-class="primary--text"
							column
						>
							<v-chip
								v-for="tt in tool.keywords.filter(e => e).slice(0, 5)"
								:key="tt"
							>
								{{ tt }}
							</v-chip>
						</v-chip-group>
					</v-card-text>

					<v-card-actions
						class="home-card-actions"
					>
						<v-row>
							<v-btn
								class="mt-4 ms-4 me-2"
								color="primary"
								dark
								:to="`/tool/${tool.id}`"
							>
								{{ $t( 'learnmore' ) }}
								<v-icon
									dark
									right
								>
									mdi-information-outline
								</v-icon>
							</v-btn>

							<v-btn
								class="mt-4"
								color="primary"
								dark
								:href="`${tool.url}`"
								target="_blank"
							>
								{{ $t( 'browsetool' ) }}
								<v-icon
									dark
									right
								>
									mdi-link-variant
								</v-icon>
							</v-btn>
						</v-row>
					</v-card-actions>
				</v-card>
			</v-row>
		</v-row>

		<v-pagination
			v-if="numTools > 0"
			v-model="page"
			:length="Math.ceil( numTools / itemsPerPage )"
			class="ma-4"
			@input="goToNextPage"
		/>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import '@/assets/styles/index.css';

export default {
	data() {
		return {
			page: 1,
			itemsPerPage: 10
		};
	},
	computed: {
		...mapState( 'tools', [ 'toolsList', 'numTools' ] )
	},
	methods: {
		listAllTools() {
			this.$store.dispatch( 'tools/listAllTools', this.page );
		},
		goToNextPage( page ) {
			this.page = page;
			this.listAllTools();
		}
	},
	mounted() {
		this.listAllTools();
	}
};
</script>
