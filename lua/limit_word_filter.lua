-- 限制词组数量，超过最大数量的长词将被丢弃
local M = {}

function M.init(env)
    local config = env.engine.schema.config
    env.name_space = env.name_space:gsub("^*", "")
    -- 默认最多允许 3 个词组
    M.max_words = config:get_int(env.name_space .. "/max_words") or 3
end

function M.func(input, env)
    local word_count = 0
    for cand in input:iter() do
        local leng = utf8.len(cand.text)
        -- 判断是否为多字词组
        if leng > 1 then
            word_count = word_count + 1
            if word_count <= M.max_words then
                yield(cand)
            end
            -- 如果超过了最大词组数量，则直接丢弃，不 yield
        else
            -- 单字不受限制
            yield(cand)
        end
    end
end

return M
