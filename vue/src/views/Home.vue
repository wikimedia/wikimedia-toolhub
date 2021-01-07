<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<v-card
					class="mx-auto"
					outlined
					elevation="1"
				>
					<v-row no-gutters>
						<v-col>
							<h2 class="display-1 ma-4">
								{{ $t( 'welcomemessage' ) }}
							</h2>
							<div class="me-4 ms-4">
								{{ $t( 'tagline-about' ) }}
							</div>
							<div class="me-4 ms-4">
								<a href="https://meta.wikimedia.org/wiki/Toolhub"
									target="_blank"
								>
									{{ $t( 'tagline-learnmore' ) }}
								</a>
							</div>

							<v-row
								v-if="lastCrawlerRun"
								class="mx-1 my-3 text--secondary subtitle-2"
							>
								<v-col
									lg="6"
									cols="12"
									class="py-0"
								>
									<v-icon size="15">
										mdi-tools
									</v-icon>
									{{ $tc( 'toolsfound', numTools ) }}
								</v-col>
								<v-col
									lg="6"
									cols="12"
									class="py-0"
								>
									<v-icon
										size="16"
										class="me-1"
									>
										mdi-update
									</v-icon>

									<a href="/crawler-history">{{ $tc( 'newtoolsfound',
										lastCrawlerRun.new_tools +
											lastCrawlerRun.updated_tools ) }}
										{{ $t( 'tools-lastupdated', { date:
											formatDate( lastCrawlerRun.end_date ) } ) }}
									</a>
								</v-col>
							</v-row>
						</v-col>
						<v-col cols="auto">
							<v-avatar
								class="ma-3"
								size="125"
								tile
							>
								<v-img src="/static/img/logo-community.svg" />
							</v-avatar>
						</v-col>
					</v-row>
				</v-card>
			</v-col>
		</v-row>
		<v-row justify="space-around">
			<v-col v-for="tool in toolsList"
				:key="tool.name"
				sm="6"
				md="4"
				lg="3"
				cols="12"
			>
				<v-card
					class="home-tool-card"
					height="550px"
				>
					<v-card-title
						class="flex-nowrap"
					>
						<v-img
							v-if="tool.icon"
							class="me-2"
							:src="tool.icon.img"
							max-height="50"
							max-width="50"
						/>
						<v-icon
							v-else
							class="me-2"
							size="50"
						>
							mdi-tools
						</v-icon>
						<div
							class="home-tool-title line-clamp"
						>
							{{ tool.title }}
						</div>
					</v-card-title>

					<v-card-text
						class="py-0"
					>
						<div class="text--primary home-tool-desc line-clamp">
							{{ tool.description }}
						</div>

						<dl class="row mx-0 my-4 subtitle-1">
							<dt class="me-1">{{ $t( 'authors' ) }}:</dt>
							<dd>{{ tool.author }}</dd>
						</dl>

						<v-divider />
					</v-card-text>

					<v-card-text
						class="py-0"
					>
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

					<v-card-actions class="ma-2">
						<v-btn
							color="primary"
							dark
							block
							:to="`/tool/${tool.name}`"
						>
							<v-icon
								dark
								class="pe-1"
							>
								mdi-information-outline
							</v-icon>
							{{ $t( 'learnmore' ) }}
						</v-btn>
						<v-spacer />
						<v-btn
							color="primary"
							dark
							block
							:href="`${tool.url}`"
							target="_blank"
						>
							<v-icon
								dark
								class="pe-1"
							>
								mdi-link-variant
							</v-icon>
							{{ $t( 'browsetool' ) }}
						</v-btn>
					</v-card-actions>
				</v-card>
			</v-col>
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

export default {
	data() {
		return {
			page: 1,
			itemsPerPage: 12
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
			return this.$moment( date ).format( 'lll' );
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
