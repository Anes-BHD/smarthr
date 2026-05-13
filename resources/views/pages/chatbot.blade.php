@extends('layouts.app')

@push('page-styles')
    <style>
        .ai-chat-card {
            border: 1px solid #e9ecef;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        }

        .ai-chat-shell {
            min-height: 560px;
            display: flex;
            flex-direction: column;
        }

        .ai-chat-header {
            padding: 18px 20px;
            border-bottom: 1px solid #f1f1f1;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .ai-chat-icon {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: #ffedf0;
            color: #ff5b6e;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            flex: 0 0 auto;
        }

        .ai-chat-title {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }

        .ai-chat-subtitle {
            margin: 2px 0 0;
            color: #6c757d;
            font-size: 13px;
        }

        .ai-chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #fafafa;
            min-height: 360px;
            max-height: 58vh;
        }

        .ai-chat-row {
            display: flex;
            margin-bottom: 14px;
        }

        .ai-chat-row.user {
            justify-content: flex-end;
        }

        .ai-chat-row.assistant {
            justify-content: flex-start;
        }

        .ai-chat-bubble {
            max-width: min(76%, 720px);
            padding: 11px 14px;
            border-radius: 16px;
            line-height: 1.45;
            word-break: break-word;
            white-space: pre-wrap;
        }

        .ai-chat-row.user .ai-chat-bubble {
            background: #ff5b6e;
            color: #fff;
            border-bottom-right-radius: 5px;
        }

        .ai-chat-row.assistant .ai-chat-bubble {
            background: #fff;
            color: #333;
            border: 1px solid #ececec;
            border-bottom-left-radius: 5px;
        }

        .ai-chat-row.error .ai-chat-bubble {
            border-color: #f5c2c7;
            color: #842029;
            background: #f8d7da;
        }

        .ai-chat-form {
            padding: 16px 20px 18px;
            border-top: 1px solid #f1f1f1;
            background: #fff;
        }

        .ai-chat-input-row {
            display: flex;
            gap: 10px;
        }

        .ai-chat-input {
            min-height: 46px;
            resize: none;
        }

        .ai-chat-send {
            min-width: 118px;
            background: #ff5b6e;
            border-color: #ff5b6e;
        }

        .ai-chat-send:hover,
        .ai-chat-send:focus {
            background: #f43f5e;
            border-color: #f43f5e;
        }

        @media (max-width: 575.98px) {
            .ai-chat-shell {
                min-height: 500px;
            }

            .ai-chat-input-row {
                flex-direction: column;
            }

            .ai-chat-send {
                width: 100%;
            }

            .ai-chat-bubble {
                max-width: 90%;
            }
        }
    </style>
@endpush

@section('page-content')
    <div class="content container-fluid">
        <!-- Page Header -->
        <x-breadcrumb>
            <x-slot name="title">{{ __('AI Assistant') }}</x-slot>
            <ul class="breadcrumb">
                <li class="breadcrumb-item"><a href="{{ route('dashboard') }}">{{ __('Dashboard') }}</a></li>
                <li class="breadcrumb-item active">{{ __('Chatbot') }}</li>
            </ul>
        </x-breadcrumb>
        <!-- /Page Header -->

        <div class="row">
            <div class="col-sm-12">
                <div class="card ai-chat-card">
                    <div class="ai-chat-shell">
                        <div class="ai-chat-header">
                            <span class="ai-chat-icon">
                                <i class="la la-comments"></i>
                            </span>
                            <div>
                                <h3 class="ai-chat-title">{{ __('AI Assistant') }}</h3>
                                <p class="ai-chat-subtitle mb-0">{{ __('Employee information assistant') }}</p>
                            </div>
                        </div>

                        <div class="ai-chat-messages" id="aiChatMessages" aria-live="polite">
                            <div class="ai-chat-row assistant">
                                <div class="ai-chat-bubble">Bonjour, je suis votre assistant SmartHR. Posez-moi une question sur les employés.</div>
                            </div>
                        </div>

                        <div class="ai-chat-form">
                            <form id="aiChatForm">
                                <div class="ai-chat-input-row">
                                    <textarea
                                        id="aiChatInput"
                                        class="form-control ai-chat-input"
                                        rows="1"
                                        autocomplete="off"
                                    ></textarea>
                                    <button type="submit" class="btn btn-primary ai-chat-send" id="aiChatSend">
                                        {{ __('Envoyer') }}
                                    </button>
                                </div>
                            </form>

                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
@endsection

@push('page-scripts')
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            var form = document.getElementById('aiChatForm');
            var input = document.getElementById('aiChatInput');
            var sendButton = document.getElementById('aiChatSend');
            var messages = document.getElementById('aiChatMessages');
            var loadingRow = null;

            function scrollToBottom() {
                messages.scrollTop = messages.scrollHeight;
            }

            function addMessage(text, sender, isError) {
                var row = document.createElement('div');
                row.className = 'ai-chat-row ' + sender + (isError ? ' error' : '');

                var bubble = document.createElement('div');
                bubble.className = 'ai-chat-bubble';
                bubble.textContent = text;

                row.appendChild(bubble);
                messages.appendChild(row);
                scrollToBottom();

                return row;
            }

            function setLoading(isLoading) {
                input.disabled = isLoading;
                sendButton.disabled = isLoading;
                sendButton.textContent = isLoading ? 'Envoi...' : 'Envoyer';

                if (isLoading) {
                    loadingRow = addMessage('L’assistant réfléchit...', 'assistant', false);
                    return;
                }

                if (loadingRow) {
                    loadingRow.remove();
                    loadingRow = null;
                }
            }

            async function sendMessage(userMessage) {
                addMessage(userMessage, 'user', false);
                setLoading(true);

                try {
                    // FastAPI doit autoriser http://127.0.0.1:8000 en CORS si le navigateur bloque cet appel.
                    var response = await fetch('http://127.0.0.1:8001/chat', {
                        method: 'POST',
                        headers: {
                            'Authorization': 'Bearer super-secret-token',
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            session_id: 'admin_chat_session',
                            message: userMessage
                        })
                    });

                    var data = await response.json();
                    setLoading(false);

                    if (!data || !data.message) {
                        addMessage('Réponse invalide de l’agent.', 'assistant', true);
                        return;
                    }

                    addMessage(data.message, 'assistant', false);
                } catch (error) {
                    setLoading(false);
                    addMessage('Impossible de contacter l’agent AI. Vérifiez que le serveur FastAPI tourne sur le port 8001.', 'assistant', true);
                }
            }

            form.addEventListener('submit', function (event) {
                event.preventDefault();

                var userMessage = input.value.trim();
                if (!userMessage) {
                    return;
                }

                input.value = '';
                sendMessage(userMessage);
            });

            input.addEventListener('keydown', function (event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    form.requestSubmit();
                }
            });

        });
    </script>
@endpush
