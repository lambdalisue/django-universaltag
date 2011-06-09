/*
 * django.universaltag.js
 * 
 * Author:		dotdister
 * Inspector: 	giginet
 * 				alisue
 *	
 */
(function($){
	// Define PUT, DELETE method
	$.extend({
		"put": function(url, data, success, error) {
			error = error || function() {};
			return $.ajax({
				"url": url,
				"data": data,
				"success": success,
				"type": "PUT",
				"cache": false,
				"error": error,
				"dataType": "json"
			});
		},
		"del": function(url, data, success, error) {
			error = error || function() {};
			return $.ajax({
				"url": url,
				"data": data,
				"success": success,
				"type": "DELETE",
				"cache": false,
				"error": error,
				"dataType": "json"
			});
		}
	});
	// Define universalTag
	$.fn.universalTag = function(settings){
		settings = $.extend(true, {
			suggestions: [],
			classes: {
				wrap:	'universaltag',
				tag:	'tag',
				frozen:	'frozen',
				tools:	'tools',
				buttons: {
					add_show:	'show',
					add_close:	"close",
					del:		'delete',
					freeze:		'freeze'
				}
			},
			urls: {
				add:	'',
				del:	'',
				freeze:	'',
				sort:	''
			},
			titles: {
				add_show:	"タグ追加フォームを表示します",
				add_close:	"タグ追加フォームを隠します",
				add_input:	"スペース・エンターで投稿します",
				del:		"タグを削除します",
				freeze:		"タグを凍結します",
				thaw:		"タグを解凍します"
			},
			plugins: {
				autocomplete:	true,
				contextmenu:	true
			},
			debug:		false
		}, settings);
		if (!settings.urls.add || !settings.urls.del || !settings.urls.freeze || !settings.urls.sort){
			if (settings.debug) {
				alert("Exception: could not found required options [will quit] (django.tagging.js)\n\n" +
					"To enable the feature of editing tags, `urls` options is required.\n" +
					"Please make sure that you have configured it correctly.\n\n"+
					"(You see this message because `debug` option is set `true`)");
			}
			return false;
		}
		return this.each(function(){
			var $ul = $(this).wrap($('<div>').addClass(settings.classes.wrap));
			if (!$ul.attr('content_type') || !$ul.attr('object_id')){
				if (settings.debug) {
					alert("Warning: wrong ul is selected (django.universaltag.js)\n\n"+
						"`ul` doesn't have custome attribute (`content_type` and `object_id`).\n"+
						"To enable the feature of editing tags, these custome attribute is reqiured.\n"+
						"Please make sure that you have configured it correctly.\n\n" +
						"(You see this message because `debug` option is set `true`)");
				}
				return false;
			}
			function generateTag(tagged_item){
				var $tag = $('<li>').addClass(settings.classes.tag);
				if(tagged_item.frozen){
					$tag.addClass(settings.classes.frozen);
				}
				$tag.append($('<a>').attr('href', tag.url).text(tag.label));
				// タグツール（削除・凍結）を追加
				addTagToolsToTag($tag);
				if (settings.plugins.contextmenu){
					// タグにコンテキストメニューを追加
					$tag.contextMenu('context-menu', initContextMenu());
				}
				return $tag;
			};
			// addDialogの初期化
			function initAddDialog(){
				var $addDialog = $('<li>').addClass(settings.classes.tools).addClass('clearfix');
				var $fieldset = $('<div>').addClass('fieldset').hide();
				var $input = $('<input>');
				var $showButton = $('<a>').addClass('button').addClass(settings.classes.buttons.add_show);
				var $closeButton = $('<a>').addClass('button').addClass(settings.classes.buttons.add_close);
				// タグの追加関数
				function postAdd(){
					post(settings.urls.add, $input.val(), function(data){
						if (data.status == 'ok'){
							$.each(data.instance_list, function(){
								var $tag = generateTag(this).hide();
								$addDialog.before($tag);
								$tag.show('fast', function(){
									$('li.tag.empty', $ul).hide('fast', function(){$(this).remove()});
								});
							});
							// 成功しているので入力欄を初期化
							$input.val('');
						} else {
							alert("Error:\n\n" + data.errors.join("\n"));
						}
					});
				};
				// フィールドセットを隠す
				function hide(){
					if ($fieldset.css('display') != 'none'){
						$fieldset.hide('fast', function(){
							$showButton.removeClass('active');
						});
					}
				};
				// フィールドセットを表示する
				function show(){
					if ($fieldset.css('display') == 'none'){
						$fieldset.show('fast', function(){
							$input.focus();
							$showButton.addClass('active');
						});
					}
				};
				if (settings.plugins.autocomplete) {
					// 入力欄の初期化処理
					$input.attr('title', settings.titles.add_input);
				}
				// 入力補佐を有効化（ required jQuery-UI autocomplete )
				if($input.autocomplete != undefined){
					$input.autocomplete({
						'source': settings.suggestions
					});
				}
				$input.keydown(function(e){
					// TODO: ダブルクオーテーション入力によるスペース・コンマ処理
					if (e.keyCode == 27){
						// ESC: キャンセル処理
						$input.val('');
						$hide();
					} else if (e.keyCode == 32 || e.keyCode == 188){
						// SPACE, COMMA: 連続投稿処理
						postAdd();
					} else if (e.keyCode == 13) {
						// ENTER: 投稿処理
						postAdd();
						$hide();
					} else {
						return true;
					}
					// 処理を行ったので入力情報を破棄
					return false;
				});
				// 入力欄表示ボタンの初期化処理
				$showButton.attr('href', 'javascript:void(0)');
				$showButton.attr('title', settings.titles.add_show);
				$showButton.click(show);
				// 入力欄クローズボタンの初期化処理
				$closeButton.attr('href', 'javascript:void(0)');
				$closeButton.attr('title', settings.titles.add_close);
				$closeButton.click(hide);
				// エレメントを追加しダイアログを作成
				$fieldset.append($input).append($closeButton);
				$addDialog.append($showButton);
				$addDialog.append($fieldset);
				return $addDialog;
			};
			// 削除ボタン
			function initDeleteButton(){
				var $button = $('<a>').addClass('button').addClass(settings.classes.buttons.del);
				$button.attr('href', 'javascript:void(0)');
				$button.attr('title', settings.titles.del);
				$button.click(function(){
					var $target = $button.parent('li.tag');
					post(settings.urls.del,'"'+$target.text()+'"', function(data){
						if(data.status == 'ok'){
							// 元データが li.tag から取ってきているため帰ってくるデータ
							// は最大で1個。したがって以下のような分岐が可能
							if (data.errors){
								alert("Error:\n\n" + data.errors.join("\n"));
							}else{
								$target.hide('fast', function(){
									$(this).remove();
									if($('li.tag', $ul).length == 0){
										// タグなし権兵衛追加
										var $tag = $('<li>').addClass(settings.classes.tag).addClass('empty');
										$tag.html("<a href='#'>タグ無し権兵衛</a>");
										$('li.'+settings.classes.tools, $ul).before($tag);
									}
								});
							}
						} else {
							alert("Exception:\n\n" + data.errors.join("\n"));
						}
					});
				});
				return $button;
			};
			// 凍結ボタン
			function initFrozeButton(){
				// 親タグの状態によりヘルプテキストを選択する関数
				function setTitle($button){
					var $tag = $button.parent('li.tag');
					if ($tag.hasClass(settings.classes.frozen)){
						$button.attr('title', settings.titles.thaw);
					}else{
						$button.attr('title', settings.titles.freeze);
					}
					return $button;
				}
				var $button = $('<a>').addClass('button').addClass(settings.classes.buttons.freeze);
				$button.attr('href', 'javascript:void(0)');
				$button = setTitle($button);
				$button.click(function(){
					var $target = $button.parent('li.tag');
					post(settings.urls.freeze, '"'+$target.text()+'"', function(data){
						if(data.status == 'ok'){
							// 元データが li.tag から取ってきているため帰ってくるデータ
							// は最大で1個。したがって以下のような分岐が可能
							if (data.errors){
								alert("Error:\n\n" + data.errors.join("\n"));
							}else{
								if(data.instance_list[0].frozen){
									$target.addClass(settings.classes.frozen);
									$('a.button.'+settings.classes.buttons.del, $target).hide('fast');
								}else{
									$target.removeClass(settings.classes.frozen);
									$('a.button.'+settings.classes.buttons.del, $target).show('fast');
								}
								$button = setTitle($button);
							}
						} else {
							alert("Error:\n\n" + data.errors.join("\n"));
						}
					});
				});
				return $button;
			};
			// タグツール（削除・凍結ボタン）をタグに追加する関数
			function addTagToolsToTag($tag){
				$tag.append(initDeleteButton());
				if ($ul.attr('owned') != ''){
					$tag.append(initFrozeButton());
					if ($tag.hasClass(settings.classes.frozen)){
						// 凍結タグは削除できない
						$('a.button.'+settings.classes.buttons.del, $tag).hide();
					}
				}
			};
			// ContextMenu
			function initContextMenu(){
				var menu = {
					"タグを削除する": {
						click: function(elm){
							$('a.button.'+settings.classes.buttons.del, $(elm)).click();
						},
						klass: settings.classes.buttons.del
					},
					"タグを凍結・解除する": {
						click: function(elm){
							$('a.button.'+settings.classes.buttons.freeze, $(elm)).click();
						},
						klass: settings.classes.buttons.freeze
					}
				};
				return menu;
			};
			// タグ追加フォームの追加
			$ul.append(initAddDialog());
			// 個々のタグに対する処理（削除・凍結）を適用
			$('li.tag:not(.empty)', $ul).each(function(){
				addTagToolsToTag($(this));
			});
			// 並び替えを可能にする
			$ul.sortable({items:"li.tag:not(.empty)", stop: function(){
				labels = "";
				$('li.tag:not(.empty)', $ul).each(function(){
					// スペース等を含むタグに対応するためにダブルクオーテーションでラップ
					labels += '"' + $(this).text() + '", ';
				});
				post(settings.urls.sort, labels);
			}});
			if (settings.plugins.contextmenu){
				// 右クリックメニューを登録する
				$('li.tag', $ul).contextMenu('context-menu', initContextMenu());
			}
		});
	};
})(jQuery);
