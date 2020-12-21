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
							<div class="me-4 ms-4">
								{{ $t( 'tagline-about' ) }}
								<a href="https://meta.wikimedia.org/wiki/Toolhub"
									target="_blank"
								>{{ $t( 'tagline-learnmore' ) }}</a>.
							</div>

							<v-card-subtitle
								v-if="lastCrawlerRun"
							>
								<v-icon
									size="15"
									class="me-1"
								>
									mdi-tools
								</v-icon>
								{{ numTools }}
								{{ $t( 'tools' ) }} {{ $t( 'found' ) }}
								•
								<v-icon
									size="16"
									class="me-2"
								>
									mdi-update
								</v-icon>

								<a href="/crawler-history">{{ $tc( 'newtoolsfound',
									lastCrawlerRun.new_tools ) }}
									{{ $t( 'tools-lastupdated', { date:
										formatDate( lastCrawlerRun.end_date ) } ) }}
								</a>
							</v-card-subtitle>
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
					min-height="450"
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
			total-visible="10"
			@input="goToPage"
		/>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import '@/assets/styles/index.css';
import moment from 'moment';

export default {
	data() {
		return {
			page: 1,
			itemsPerPage: 10
		};
	},
	computed: {
		...mapState( 'tools', [ 'toolsList', 'numTools' ] ),
		...mapState( 'crawler', [ 'crawlerHistory', 'lastCrawlerRun', 'numCrawlerRuns' ] )
	},
	methods: {
		listAllTools() {
			this.$store.dispatch( 'tools/listAllTools', this.page );
		},
		fetchCrawlerHistory() {
			this.$store.dispatch( 'crawler/fetchCrawlerHistory', 1 );
		},
		goToPage( num ) {
			this.page = num;
			this.listAllTools();

			this.$router.push( {
				query: { page: this.page }
			} ).catch( () => {} );
		},
		formatDate( date ) {
			return moment( date ).format( 'lll' );
		}
	},
	mounted() {
		this.page = parseInt( this.$route.query.page ) || 1;

		this.listAllTools();
		this.fetchCrawlerHistory();

		window.onpopstate = () => {
			const params = ( new URL( document.location ) ).searchParams;
			let pageNum = parseInt( params.get( 'page' ) );

			if ( !pageNum ) {
				pageNum = 1;
			}

			this.goToPage( pageNum );
		};
	}
};
</script>
